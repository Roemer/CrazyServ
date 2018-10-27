from enum import Enum, auto
import time
import math
import threading
import numpy as np

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.utils.callbacks import Caller


from .arena import Arena


class DroneState(Enum):
    IDLE = auto()
    OFFLINE = auto()
    HOVERING = auto()
    STARTING = auto()
    LANDING = auto()
    NAVIGATING = auto()


class Drone:
    """Represents a CrazyFlie drone."""

    def __init__(self, drone_id: str,  arena: Arena, radio_id: int = 0, channel: int = 80, address: str = "E7E7E7E7E7", data_rate: str = "2M"):
        """ Initializes the drone with the given uri."""

        # Initialize public variables
        self.id: str = drone_id
        self.var_x: float = 0
        self.var_y: float = 0
        self.var_z: float = 0
        self.pos_x: float = 0
        self.pos_y: float = 0
        self.pos_z: float = 0
        self.yaw: float = 0
        self.battery_voltage: float = 0
        self.is_connected: bool = False
        self.status: DroneState = DroneState.OFFLINE
        self.link_uri: str = "radio://" + str(radio_id) + "/" + str(channel) + "/" + data_rate + "/" + address

        # Initialize limits
        self._max_velocity: float = 1.0
        self._min_duration: float = 1.0
        self._max_yaw_rotations: float = 1.0
        self._arena = arena

        # Event to asynchronously wait for the connection
        self._connect_event = threading.Event()

        # Initialize the crazyflie
        self._cf = Crazyflie(rw_cache='./cache')

        # Initialize the callbacks
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        # Initialize events
        self.drone_lost = Caller()

        # Define the log configuration
        self._log_config_1 = LogConfig(name='DroneLog_1', period_in_ms=500)
        self._log_config_1.add_variable('kalman.varPX', 'float')
        self._log_config_1.add_variable('kalman.varPY', 'float')
        self._log_config_1.add_variable('kalman.varPZ', 'float')
        self._log_config_1.add_variable('pm.vbat', 'float')
        self._log_config_2 = LogConfig(name='DroneLog_2', period_in_ms=500)
        self._log_config_2.add_variable('kalman.stateX', 'float')
        self._log_config_2.add_variable('kalman.stateY', 'float')
        self._log_config_2.add_variable('kalman.stateZ', 'float')
        self._log_config_2.add_variable('stabilizer.yaw', 'float')

    def connect(self, synchronous: bool = False):
        """Connects to the Crazyflie."""
        self._connect_crazyflie()
        if synchronous:
            self._connect_event.wait()

    def disconnect(self):
        """Disconnects from the Crazyflie and stops all logging."""
        self._disconnect_crazyflie()

    def enable_high_level_commander(self):
        """Enables the drones high level commander."""
        self._cf.param.set_value('commander.enHighLevel', '1')
        time.sleep(0.1)

    def disable_motion_tracking(self):
        """Disables to motion control (x/y) from the flow-deck."""
        self._cf.param.set_value('motion.disable', '1')
        time.sleep(0.1)

    def get_status(self) -> str:
        """Gets various information of the drone."""
        return {
            "id": self.id,
            "var_x": self.var_x,
            "var_y": self.var_y,
            "var_z": self.var_z,
            "x": self._arena.transform_x_inverse(self.pos_x),
            "y": self._arena.transform_y_inverse(self.pos_y),
            "z": self.pos_z,
            "yaw": self.yaw,
            "status": self.status.name,
            "battery_voltage": self.battery_voltage,
            "battery_percentage:": (self.battery_voltage - 3.4) / (4.18 - 3.4) * 100
        }

    def reset_estimator(self) -> bool:
        """Resets the position estimates."""
        self._cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2.0)
        # TODO: wait_for_position_estimator(cf)
        return True

    def takeoff(self, absolute_height: float, velocity: float, synchronous: bool = False) -> float:
        absolute_height = self._sanitize_z(absolute_height, False)
        self.reset_estimator()
        duration = self._convert_velocity_to_time(absolute_height, velocity)
        self._cf.high_level_commander.takeoff(absolute_height, duration)
        self.status = DroneState.STARTING
        if synchronous:
            time.sleep(duration)
        return {
            "duration": duration,
            "target_z": absolute_height
        }

    def land(self, absolute_height: float, velocity: float, synchronous: bool = False) -> float:
        absolute_height = self._sanitize_z(absolute_height, False)
        duration = self._convert_velocity_to_time(absolute_height, velocity)
        self._cf.high_level_commander.land(absolute_height, duration)
        self.status = DroneState.LANDING
        if synchronous:
            time.sleep(duration)
        return {
            "duration": duration,
            "target_z": absolute_height
        }

    def go_to(self, x: float, y: float, z: float, yaw: float, velocity: float, relative: bool = False, synchronous: bool = False) -> float:
        x = self._sanitize_x(x, relative)
        y = self._sanitize_y(y, relative)
        z = self._sanitize_z(z, relative)
        yaw = self._sanitize_yaw(yaw)
        distance = self._calculate_distance(x, y, z, relative)
        duration = self._convert_velocity_to_time(distance, velocity)
        self._cf.high_level_commander.go_to(x, y, z, yaw, duration, relative)
        self.status = DroneState.NAVIGATING
        if synchronous:
            time.sleep(duration)
        return {
            "duration": duration,
            "target_x": x,
            "target_y": y,
            "target_z": z,
            "target_yaw": yaw,
            "relative": relative
        }

    def stop(self):
        self._cf.high_level_commander.stop()
        self.status = DroneState.IDLE

    def _connect_crazyflie(self):
        print('Connecting to %s' % self.link_uri)
        self._cf.open_link(self.link_uri)

    def _disconnect_crazyflie(self):
        print('Disconnecting from %s' % self.link_uri)
        # Stop the loggers
        self._log_config_1.stop()
        self._log_config_2.stop()
        # Shutdown the rotors
        self._shutdown()
        # Disconnect
        self._cf.close_link()

    def _connected(self, link_uri):
        """This callback is called when the Crazyflie has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)
        # Setup parameters
        self.disable_motion_tracking()
        # Add the logger
        self._cf.log.add_config(self._log_config_1)
        self._cf.log.add_config(self._log_config_2)
        # This callback will receive the data
        self._log_config_1.data_received_cb.add_callback(self._log_config_1_data)
        self._log_config_2.data_received_cb.add_callback(self._log_config_2_data)
        # This callback will be called on errors
        self._log_config_1.error_cb.add_callback(self._log_config_error)
        self._log_config_2.error_cb.add_callback(self._log_config_error)
        # Start the logging
        self._log_config_1.start()
        self._log_config_2.start()
        # Set the connected event
        self._connect_event.set()
        self.is_connected = True
        self.status = DroneState.IDLE

    def _connection_failed(self, link_uri, msg):
        """Callback when the initial connection fails."""
        print('Connection to %s failed: %s' % (link_uri, msg))
        # Set the connected event
        self._connect_event.set()

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected."""
        print('Disconnected from %s' % link_uri)
        self.is_connected = False
        self.status = DroneState.OFFLINE

    def _connection_lost(self, link_uri, msg):
        """Callback when the connection is lost after a connection has been made."""
        print('Connection to %s lost: %s' % (link_uri, msg))
        self.drone_lost.call(self)
        self._connect_event.set()
        self.is_connected = False
        self.status = DroneState.OFFLINE

    def _log_config_error(self, logconf, msg):
        """Callback from the log API when an error occurs."""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _log_config_1_data(self, timestamp, data, logconf):
        """Callback from the log API when data arrives."""
        self.var_x = data['kalman.varPX']
        self.var_y = data['kalman.varPY']
        self.var_z = data['kalman.varPZ']
        self.battery_voltage = data['pm.vbat']

    def _log_config_2_data(self, timestamp, data, logconf):
        """Callback from the log API when data arrives."""
        self.pos_x = data['kalman.stateX']
        self.pos_y = data['kalman.stateY']
        self.pos_z = data['kalman.stateZ']
        self.yaw = data['stabilizer.yaw']

    def _unlock(self):
        # Unlock startup thrust protection (only needed for low lewel commands)
        self._cf.commander.send_setpoint(0, 0, 0, 0)

    def _shutdown(self):
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)

    def _keep_setpoint(self, roll, pitch, yawrate, thrust, keeptime):
        """Keeps the drone at the given setpoint for the given amount of time."""
        while keeptime > 0:
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            keeptime -= 0.1
            time.sleep(0.1)

    def _convert_velocity_to_time(self, distance: float, velocity: float) -> float:
        """Converts a distance and a velocity to a time."""
        duration = distance / self._sanitize_velocity(velocity)
        return self._sanitize_duration(duration)

    def _calculate_distance(self, x: float, y: float, z: float, relative: bool = False) -> float:
        """Calculates the distance from the drone or the zero position (relative) to a given point in space."""
        start_x = 0 if relative else self.pos_x
        start_y = 0 if relative else self.pos_y
        start_z = 0 if relative else self.pos_z
        return np.sqrt((x - start_x) ** 2 + (y - start_y) ** 2 + (z - start_z) ** 2)

    def _sanitize_velocity(self, velocity: float) -> float:
        return min(velocity, self._max_velocity)

    def _sanitize_duration(self, duration: float) -> float:
        return max(duration, self._min_duration)

    def _sanitize_yaw(self, yaw: float) -> float:
        return yaw % (2 * self._max_yaw_rotations * math.pi)

    def _sanitize_x(self, x: float, relative: bool) -> float:
        target_x = (self.pos_x + x) if relative else x
        sanitized_x = self._sanitize_number(target_x, self._arena.min_x, self._arena.max_x)
        return self._arena.transform_x(sanitized_x)

    def _sanitize_y(self, y: float, relative: bool) -> float:
        target_y = (self.pos_y + y) if relative else y
        sanitized_y = self._sanitize_number(target_y, self._arena.min_y, self._arena.max_y)
        return self._arena.transform_y(sanitized_y)

    def _sanitize_z(self, z: float, relative: bool) -> float:
        return self._sanitize_number(z, self._arena.min_z, self._arena.max_z)

    def _sanitize_number(self, value: float, min_value: float, max_value: float) -> float:
        return min(max(value, min_value), max_value)
