import time
from threading import Event

from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig


class Drone:
    """ Represents a CrazyFlie drone """

    def __init__(self, link_uri):
        """ Initializes the drone with the given uri """

        # Initialize public variables
        self.var_x = 0
        self.var_y = 0
        self.var_z = 0
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        self.is_connected = False
        self.link_uri = link_uri
        self.link_uri = 'radio://0/80/2M'

        self._connect_event = Event()

        # Initialize the crazyflie
        self._cf = Crazyflie(rw_cache='./cache')

        # Initialize the callbacks
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        # Define the log configuration
        self._lg_stab = LogConfig(name='Kalman', period_in_ms=500)
        self._lg_stab.add_variable('kalman.varPX', 'float')
        self._lg_stab.add_variable('kalman.varPY', 'float')
        self._lg_stab.add_variable('kalman.varPZ', 'float')
        self._lg_stab.add_variable('kalman.stateX', 'float')
        self._lg_stab.add_variable('kalman.stateY', 'float')
        self._lg_stab.add_variable('kalman.stateZ', 'float')

    def connect(self):
        """ Connects to the Crazyflie asynchronously """
        self._connect_crazyflie()

    def connectSync(self):
        """ Connects to the Crazyflie synchronously """
        self._connect_crazyflie()
        self._connect_event.wait()

    def disconnect(self):
        """ Disconnects from the Crazyflie and stops all logging """
        self._disconnect_crazyflie()

    def enableHighLevelCommander(self):
        self._cf.param.set_value('commander.enHighLevel', '1')
        time.sleep(0.1)

    def takeoff(self, absolute_height_m, duration_s):
        self._cf.high_level_commander.takeoff(absolute_height_m, duration_s)

    def takeoffSync(self, absolute_height_m, duration_s):
        self.takeoff(absolute_height_m, duration_s)
        time.sleep(duration_s)

    def land(self, absolute_height_m, duration_s):
        self._cf.high_level_commander.land(absolute_height_m, duration_s)

    def landSync(self, absolute_height_m, duration_s):
        self.land(absolute_height_m, duration_s)
        time.sleep(duration_s)

    def go_to(self, x, y, z, yaw, duration_s, relative=False):
        self._cf.high_level_commander.go_to(x, y, z, yaw, duration_s, relative)

    def go_toSync(self, x, y, z, yaw, duration_s, relative=False):
        self.go_to(x, y, z, yaw, duration_s, relative)
        time.sleep(duration_s)

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
        """ This callback is called when the Crazyflie has been connected and the TOCs have been downloaded. """
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
        """Callback when the initial connection fails """
        print('Connection to %s failed: %s' % (link_uri, msg))
        # Set the connected event
        self._connect_event.set()

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected """
        print('Disconnected from %s' % link_uri)

    def _connection_lost(self, link_uri, msg):
        """Callback when the connection is lost after a connection has been made """
        print('Connection to %s lost: %s' % (link_uri, msg))
        self._connect_event.set()
        self.is_connected = False

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback from the log API when data arrives"""
        #print('[%s][%d][%s]: %s' % (logconf.cf.link_uri, timestamp, logconf.name, data))
        self.var_x = data['kalman.varPX']
        self.var_y = data['kalman.varPY']
        self.var_z = data['kalman.varPZ']
        self.pos_x = data['kalman.stateX']
        self.pos_y = data['kalman.stateY']
        self.pos_z = data['kalman.stateZ']

    def _unlock(self):
        # Unlock startup thrust protection
        self._cf.commander.send_setpoint(0, 0, 0, 0)

    def _shutdown(self):
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        # Make sure that the last packet leaves before the link is closed
        # since the message queue is not flushed before closing
        time.sleep(0.1)

    def _keep_setpoint(self, roll, pitch, yawrate, thrust, keeptime):
        while keeptime > 0:
            self._cf.commander.send_setpoint(roll, pitch, yawrate, thrust)
            keeptime -= 0.1
            time.sleep(0.1)
