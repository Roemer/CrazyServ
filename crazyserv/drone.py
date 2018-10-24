import time
from threading import Event
import numpy as np

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.utils.callbacks import Caller


class Drone:
    """Represents a CrazyFlie drone."""

    def __init__(self, drone_id, bandwidth="2M"):
        """ Initializes the drone with the given uri."""

        # Initialize public variables
        self.id = drone_id
        self.var_x: float = 0
        self.var_y: float = 0
        self.var_z: float = 0
        self.pos_x: float = 0
        self.pos_y: float = 0
        self.pos_z: float = 0
        self.yaw: float = 0
        self.is_connected = False
        self.link_uri = "radio://0/" + drone_id + "/" + bandwidth

        self._connect_event = Event()

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
        self._lg_stab = LogConfig(name='DroneLog', period_in_ms=500)
        self._lg_stab.add_variable('kalman.varPX', 'float')
        self._lg_stab.add_variable('kalman.varPY', 'float')
        self._lg_stab.add_variable('kalman.varPZ', 'float')
        self._lg_stab.add_variable('kalman.stateX', 'float')
        self._lg_stab.add_variable('kalman.stateY', 'float')
        self._lg_stab.add_variable('kalman.stateZ', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')

    def connect(self):
        """Connects to the Crazyflie asynchronously."""
        self._connect_crazyflie()

    def connect_sync(self):
        """Connects to the Crazyflie synchronously."""
        self._connect_crazyflie()
        self._connect_event.wait()

    def disconnect(self):
        """Disconnects from the Crazyflie and stops all logging."""
        self._disconnect_crazyflie()

    def enable_high_level_commander(self):
        """Enables the drones high level commander."""
        self._cf.param.set_value('commander.enHighLevel', '1')
        time.sleep(0.1)

    def get_status(self) -> str:
        """Gets various information of the drone."""
        return {
            "id": self.id,
            "var_x": self.var_x,
            "var_y": self.var_y,
            "var_z": self.var_z,
            "x": self.pos_x,
            "y": self.pos_y,
            "z": self.pos_z,
            "yaw": self.yaw
        }

    def reset_estimator(self) -> bool:
        """Resets the position estimates."""
        self._cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.1)
        self._cf.param.set_value('kalman.resetEstimation', '0')
        time.sleep(2.0)
        # TODO: wait_for_position_estimator(cf)
        return True

    def takeoff(self, absolute_height_m, velocity) -> float:
        self.reset_estimator()
        duration_s = self._convert_velocity_to_time(absolute_height_m, velocity)
        self._cf.high_level_commander.takeoff(absolute_height_m, duration_s)
        return duration_s

    def takeoff_sync(self, absolute_height_m, velocity) -> float:
        duration_s = self.takeoff(absolute_height_m, velocity)
        time.sleep(duration_s)
        return duration_s

    def land(self, absolute_height_m, velocity) -> float:
        duration_s = self._convert_velocity_to_time(absolute_height_m, velocity)
        self._cf.high_level_commander.land(absolute_height_m, duration_s)
        return duration_s

    def land_sync(self, absolute_height_m, velocity) -> float:
        duration_s = self.land(absolute_height_m, velocity)
        time.sleep(duration_s)
        return duration_s

    def go_to(self, x, y, z, yaw, velocity, relative=False) -> float:
        distance = self._calculate_distance(x, y, z, relative)
        duration_s = self._convert_velocity_to_time(distance, velocity)
        self._cf.high_level_commander.go_to(x, y, z, yaw, duration_s, relative)
        return duration_s

    def go_to_sync(self, x, y, z, yaw, velocity, relative=False) -> float:
        duration_s = self.go_to(x, y, z, yaw, velocity, relative)
        time.sleep(duration_s)
        return duration_s

    def stop(self):
        self._cf.high_level_commander.stop()

    def _connect_crazyflie(self):
        print('Connecting to %s' % self.link_uri)
        self._cf.open_link(self.link_uri)

    def _disconnect_crazyflie(self):
        print('Disconnecting from %s' % self.link_uri)
        # Stop the logger
        self._lg_stab.stop()
        # Shutdown the rotors
        self._shutdown()
        # Disconnect
        self._cf.close_link()

    def _connected(self, link_uri):
        """This callback is called when the Crazyflie has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)
        # Add the logger
        self._cf.log.add_config(self._lg_stab)
        # This callback will receive the data
        self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
        # This callback will be called on errors
        self._lg_stab.error_cb.add_callback(self._stab_log_error)
        # Start the logging
        self._lg_stab.start()
        # Set the connected event
        self._connect_event.set()
        self.is_connected = True

    def _connection_failed(self, link_uri, msg):
        """Callback when the initial connection fails."""
        print('Connection to %s failed: %s' % (link_uri, msg))
        # Set the connected event
        self._connect_event.set()

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected."""
        print('Disconnected from %s' % link_uri)

    def _connection_lost(self, link_uri, msg):
        """Callback when the connection is lost after a connection has been made."""
        print('Connection to %s lost: %s' % (link_uri, msg))
        self.drone_lost.call(self)
        self._connect_event.set()
        self.is_connected = False

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs."""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback from the log API when data arrives."""
        self.var_x = data['kalman.varPX']
        self.var_y = data['kalman.varPY']
        self.var_z = data['kalman.varPZ']
        self.pos_x = data['kalman.stateX']
        self.pos_y = data['kalman.stateY']
        self.pos_z = data['kalman.stateZ']
        self.yaw = data['stabilizer.yaw']

    def _unlock(self):
        # Unlock startup thrust protection
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

    def _convert_velocity_to_time(self, distance, velocity, max_velocity=0.2) -> float:
        """Converts a distance and a velocity to a time."""
        needed_time = float(distance) / min(velocity, max_velocity)
        return needed_time

    def _calculate_distance(self, x, y, z, relative=False) -> float:
        """Calculates the distance from the drone or the zero position (relative) to a given point in space."""
        start_x = 0 if relative else self.pos_x
        start_y = 0 if relative else self.pos_y
        start_z = 0 if relative else self.pos_z
        return np.sqrt((x - start_x) ** 2 + (y - start_y) ** 2 + (z - start_z) ** 2)
