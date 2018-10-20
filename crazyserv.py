from flask import Flask, request, jsonify, abort
import cflib
from crazyserv import drone
from crazyserv.drone import Drone
from crazyserv import group
from crazyserv.group import Group
from crazyserv import groupmanager
from crazyserv.groupmanager import GroupManager

##############################
# Globals (cough)
##############################
app = Flask(__name__)
groupManager = GroupManager()

##############################
# Route Definitions
##############################


@app.route("/")
def hello():
    return "Welcome to CrazyServ!"


@app.route("/api/<groupId>/status")
def status(groupId):
    global groupManager
    group = groupManager.getGroup(groupId)
    if group is None:
        abort(404, description="Group not found.")
        return
    for drone in group.drones:
        print(drone.var_x)
    return jsonify({"group": group.id})


@app.route("/api/<groupId>/<droneId>/connect")
def connect(groupId, droneId):
    global groupManager
    # Try to create and connect to the drone
    droneLinkUri = "radio://0/" + droneId + "/2M"
    drone = Drone(droneLinkUri)
    drone.connectSync()
    # Check if the connection to the drone was successfull
    if (not drone.is_connected):
        # Connection failed
        abort(500, "Could not connect to drone.")
        return
    # Connection successfull, add the drone to the group
    drone.enableHighLevelCommander()
    group = groupManager.getOrAddGroup(groupId)
    group.addDrone(drone)
    return jsonify({'group': group.id})


@app.route("/api/<groupId>/<droneId>/takeoff")
def takeoff(groupId, droneId):
    z = request.args.get("z")
    v = request.args.get("v")
    for group in groupManager.groups:
        for drone in group.drones:
            # TODO: Search correct drone
            drone.takeoff(z, 1)
            return jsonify({'expectedDuration': 1})


@app.route("/api/<groupId>/<droneId>/land")
def land(groupId, droneId):
    z = request.args.get("z")
    v = request.args.get("v")
    for group in groupManager.groups:
        for drone in group.drones:
            # TODO: Search correct drone
            drone.land(z, 1)
            return jsonify({'expectedDuration': 1})


@app.route("/api/<groupId>/<droneId>/stop")
def stop(groupId, droneId):
    for group in groupManager.groups:
        for drone in group.drones:
            # TODO: Search correct drone
            drone.stop()
            return '', 200


@app.route("/api/<groupId>/<droneId>/goto")
def goto(groupId, droneId):
    x = request.args.get("x")
    y = request.args.get("y")
    z = request.args.get("z")
    yaw = request.args.get("yaw")
    v = request.args.get("v")
    for group in groupManager.groups:
        for drone in group.drones:
            # TODO: Search correct drone
            drone.go_to(x, y, z, yaw, 1)
            return jsonify({'expectedDuration': 1})


@app.route('/shutdown', methods=['GET'])
def shutdown():
    # Cleanup
    for group in groupManager.groups:
        for drone in group.drones:
            drone.disconnect()
    # Shutdown the server
    shutdown_server()
    return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


##############################
# Main
##############################
if __name__ == '__main__':
    port = 5000
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Start the web server
    app.run(debug=True, port=port)

'''
# Status
/status
# Response
[
    {
        "id": "80"
        "x": 2,
        "y": 2,
        "z": 2,
        "yaw": 0,
        "varx": 2,
        "vary": 2,
        "varz": 2,
    }
]
'''
