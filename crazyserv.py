import platform
from flask import Flask, request, jsonify, abort
import cflib
from crazyserv import Drone
from crazyserv import Group
from crazyserv import GroupManager
from crazyserv import Arena

##############################
# Globals (cough)
##############################
app = Flask(__name__)
group_manager = GroupManager()

##############################
# Route Definitions
##############################


@app.route("/")
def hello():
    return "Welcome to CrazyServ!"


@app.route("/api/<groupId>/status")
def status(groupId):
    group = group_manager.get_group(groupId)
    if group is None:
        abort(404, description="Group not found.")
        return
    group_status = "["
    for drone in group.drones:
        group_status += drone.get_status()
        group_status += ","
    group_status = group_status[0:-1]
    group_status += "]"
    return group_status, 200


@app.route("/api/<groupId>/<droneId>/connect")
def connect(groupId, droneId):
    global group_manager
    # Try to create and connect to the drone
    drone = Drone(droneId)
    drone.connect_sync()
    # Check if the connection to the drone was successfull
    if (not drone.is_connected):
        # Connection failed
        abort(500, "Could not connect to drone.")
        return
    # Connection successfull, add the drone to the group
    drone.enable_high_level_commander()
    drone.reset_estimator()
    group = group_manager.get_or_add_group(groupId)
    group.add_drone(drone)
    return jsonify({'group': group.id})


@app.route("/api/<groupId>/<droneId>/disconnect")
def disconnect(groupId, droneId):
    drone = group_manager.get_drone(groupId, droneId)
    drone.disconnect()
    group = group_manager.get_or_add_group(groupId)
    group.remove_drone(drone)
    return jsonify({'group': groupId})


@app.route("/api/<groupId>/<droneId>/calibrate")
def calibrate(groupId, droneId):
    drone = group_manager.get_drone(groupId, droneId)
    drone.reset_estimator()
    return jsonify({'group': groupId})


@app.route("/api/<groupId>/<droneId>/takeoff")
def takeoff(groupId, droneId):
    z = float(request.args.get("z"))
    v = float(request.args.get("v"))

    drone = group_manager.get_drone(groupId, droneId)
    drone.takeoff(z, v)

    return jsonify({'expectedDuration': 1})


@app.route("/api/<groupId>/<droneId>/land")
def land(groupId, droneId):
    z = float(request.args.get("z"))
    v = float(request.args.get("v"))

    drone = group_manager.get_drone(groupId, droneId)
    drone.land(z, v)

    return jsonify({'expectedDuration': 1})


@app.route("/api/<groupId>/<droneId>/stop")
def stop(groupId, droneId):
    drone = group_manager.get_drone(groupId, droneId)
    drone.stop()

    return '', 200


@app.route("/api/<groupId>/<droneId>/goto")
def goto(groupId, droneId):
    x = float(request.args.get("x"))
    y = float(request.args.get("y"))
    z = float(request.args.get("z"))
    yaw = float(request.args.get("yaw"))
    v = float(request.args.get("v"))

    drone = group_manager.get_drone(groupId, droneId)
    drone.go_to(x, y, z, yaw, v)

    return jsonify({'expectedDuration': 1})


@app.route('/shutdown', methods=['GET'])
def shutdown():
    # Cleanup
    for group in group_manager.groups:
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
    pc_name = platform.node()
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Start the web server
    app.run(host=pc_name, debug=True, port=port)
