import platform
from flask import Flask, request, jsonify, abort
from flasgger import Swagger, swag_from
import cflib
from crazyserv import Drone
from crazyserv import Swarm
from crazyserv import SwarmManager
from crazyserv import Arena
from crazyserv import PackageGenerator
from crazyserv import DeliveryLogger

##############################
# Globals (cough)
##############################
app = Flask(__name__)
swagger = Swagger(app)
swarm_manager = SwarmManager()
package_generator = PackageGenerator()
default_velocity = 0.2
default_start_z = 1
default_land_z = 0
default_yaw = 0

##############################
# Route Definitions
##############################


@app.route("/")
def hello():
    return "Welcome to CrazyServ!"


@app.route("/api/arena")
@swag_from("static/swagger-doc/arena.yml")
def arena():
    arena = Arena(0)
    return jsonify({
        'min_x': arena.min_x,
        'max_x': arena.max_x,
        'min_y': arena.min_y,
        'max_y': arena.max_y,
        'min_z': arena.min_z,
        'max_z': arena.max_z,
        'buildings': [[2., 2.8, 0], [1.5, 1., 0], [3.15, 0.7, 0], [3., 2., 0]]
    })


@app.route("/api/help")
@swag_from("static/swagger-doc/help.yml")
def help():
    help_text = """
    <html>
    <head>
    <title>Markdown Snippet</title>
    </head>
    <body>
    In order for you to get started with flying a drone, follow these steps: </br>
        * Register a swarm for an arena ´/api/test-swarm/register_swarm?arena_id=0&seed=12345´ </br>
        * Connect to a drone ´/api/test-swarm/test-drone/connect?r=1&c=80&a=E7E7E7E7´ </br>
        * Hover above ground ´/api/test-swarm/test-drone/takeoff?z=0.5&v=0.1´ </br>
        * Go to a position ´/api/test-swarm/test-drone/goto?x=1&y=1&z=0.5&yaw=0&v=0.1´ </br>
        * Order a parcel ´/api/test-swarm/package´ </br>
        * Pickup a parcel ´/api/test-swarm/test-drone/pickup?package_id=abcd´ </br>
        * Deliver a parcel ´/api/test-swarm/test-drone/deliver?package_id=abcd´ </br>
        * Land ´/api/test-swarm/test-drone/land?z=0.0&v=0.1´ </br>
        * Disconnect from a drone ´/api/test-swarm/test-drone/disconnect´
    </body>
    </html>"""

    return help_text


@app.route("/api/<swarm_id>/status")
@swag_from("static/swagger-doc/swarm_status.yml")
def status(swarm_id: str):
    swarm = swarm_manager.get_swarm(swarm_id)
    if swarm is None:
        abort(404, description="Swarm not found.")
    drone_stats = []
    for _, drone in swarm.drones.items():
        drone_stats.append(drone.get_status())
    return jsonify(drone_stats)


@app.route("/api/<swarm_id>/<drone_id>/status")
@swag_from("static/swagger-doc/swarm_drone_status.yml")
def drone_status(swarm_id, drone_id):
    swarm = swarm_manager.get_swarm(swarm_id)
    if swarm is None:
        abort(404, description="Swarm not found.")
    drone = swarm.get_drone(drone_id)
    if drone is None:
        abort(404, description="Drone not found.")
    return jsonify(drone.get_status())


@app.route("/api/<swarm_id>/<drone_id>/connect")
@swag_from("static/swagger-doc/connect.yml")
def connect(swarm_id, drone_id):
    radio_id = int(is_none(request.args.get("r"), 0))
    channel = int(is_none(request.args.get("c"), 80))
    address = is_none(request.args.get("a"), "E7E7E7E7E7")
    data_rate = is_none(request.args.get("dr"), "2M")

    added_drone = swarm_manager.add_drone(swarm_id, drone_id, radio_id, channel, address, data_rate)
    # Check if the connection to the drone was successfull
    if added_drone is None:
        # Connection failed
        abort(500, "Could not connect to drone.")
    return jsonify(added_drone.get_status())


@app.route("/api/<swarm_id>/<drone_id>/disconnect")
@swag_from("static/swagger-doc/disconnect.yml")
def disconnect(swarm_id, drone_id):
    drone_removed = swarm_manager.remove_drone(swarm_id, drone_id)
    return jsonify({'success': drone_removed})


@app.route("/api/<swarm_id>/<drone_id>/calibrate")
@swag_from("static/swagger-doc/calibrate.yml")
def calibrate(swarm_id, drone_id):
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    if (drone is None):
        abort(404, description="Drone not found.")
    resetted = drone.reset_estimator()
    return jsonify({'success': resetted})


@app.route("/api/<swarm_id>/<drone_id>/takeoff")
@swag_from("static/swagger-doc/takeoff.yml")
def takeoff(swarm_id, drone_id):
    z = float(is_none(request.args.get("z"), default_start_z))
    v = float(is_none(request.args.get("v"), default_velocity))
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    if (drone is None):
        abort(404, description="Drone not found.")
    takeoff_result = drone.takeoff(z, v)
    return jsonify(takeoff_result)


@app.route("/api/<swarm_id>/<drone_id>/land")
@swag_from("static/swagger-doc/land.yml")
def land(swarm_id, drone_id):
    z = float(is_none(request.args.get("z"), default_land_z))
    v = float(is_none(request.args.get("v"), default_velocity))
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    if (drone is None):
        abort(404, description="Drone not found.")
    land_result = drone.land(z, v)
    return jsonify(land_result)


@app.route("/api/<swarm_id>/<drone_id>/stop")
@swag_from("static/swagger-doc/stop.yml")
def stop(swarm_id, drone_id):
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    if (drone is None):
        abort(404, description="Drone not found.")
    drone.stop()
    return jsonify(drone.get_status())


@app.route("/api/<swarm_id>/<drone_id>/goto")
@swag_from("static/swagger-doc/goto.yml")
def goto(swarm_id, drone_id):
    x = float(request.args.get("x"))
    y = float(request.args.get("y"))
    z = float(is_none(request.args.get("z"), default_start_z))
    yaw = float(is_none(request.args.get("yaw"), default_yaw))
    velocity = float(is_none(request.args.get("v"), default_velocity))
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    if (drone is None):
        abort(404, description="Drone not found.")
    go_to_result = drone.go_to(x, y, z, yaw, velocity)
    return jsonify(go_to_result)


@app.route('/shutdown', methods=['GET'])
@swag_from("static/swagger-doc/shutdown.yml")
def shutdown():
    # Cleanup
    for swarm in swarm_manager.swarms:
        for drone in swarm.drones:
            swarm.remove_drone(drone.id)
    # Shutdown the server
    shutdown_server()
    return 'Server shutting down...'


@app.route('/api/<swarm_id>/reset_package_generator')
@swag_from("static/swagger-doc/reset_package_generator.yml")
def reset_package_generator(swarm_id):
    seed = int(is_none(request.args.get("seed"), 1))
    result = package_generator.initialize_swarm(swarm_id, seed)
    return jsonify({'success': result})


@app.route("/api/<swarm_id>/register_swarm")
@swag_from("static/swagger-doc/register_swarm.yml")
def register_swarm(swarm_id):
    arena_id = int(request.args.get("arena_id"))
    seed = int(is_none(request.args.get("seed"), 1))
    result = swarm_manager.register_swarm(swarm_id, arena_id)
    package_generator.initialize_swarm(swarm_id, seed)
    return jsonify({'success': result})


@app.route('/api/<swarm_id>/package')
@swag_from("static/swagger-doc/package_order.yml")
def coordinate(swarm_id):
    package = None
    try:
        package = package_generator.get_package(swarm_id)
    except:
        abort(404, description="Swarm not found.")
    if package is None:
        abort(500, description="Too many parcels pending.")
    return jsonify({'id': package['id'], 'coordinates': package['coordinates'], 'weight': package['weight']})


@app.route('/api/<swarm_id>/<drone_id>/pickup')
@swag_from("static/swagger-doc/pickup.yml")
def pickup(swarm_id, drone_id):
    package_id = str(request.args.get("package_id"))
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    success = package_generator.pickup(swarm_id, package_id, drone)
    return jsonify({'success': success})


@app.route('/api/<swarm_id>/<drone_id>/deliver')
@swag_from("static/swagger-doc/deliver.yml")
def deliver(swarm_id, drone_id):
    package_id = str(request.args.get("package_id"))
    drone = swarm_manager.get_drone(swarm_id, drone_id)
    success = package_generator.deliver(swarm_id, package_id, drone)
    return jsonify({'success': success})


@app.route('/api/<swarm_id>/print_deliveries')
@swag_from("static/swagger-doc/print_deliveries.yml")
def print(swarm_id):
    success = package_generator.print_deliveries(swarm_id)
    return jsonify({'success': success})


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def is_none(value, alternative):
    if value is None:
        return alternative
    else:
        return value


##############################
# Main
##############################
if __name__ == '__main__':
    port = 5000
    host = "0.0.0.0"
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Start the web server
    app.run(host=host, debug=True, port=port)
