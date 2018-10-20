import threading
from flask import Flask, request, jsonify, abort

##############################
# Classes
##############################


class Groups:
    """ Class that handles the list of groups. """

    def __init__(self):
        self.groups = []
        self.lock = threading.Lock()

    def getGroup(self, groupId):
        """ Returns the group with the given id or None if such a group does not exist. """
        self.lock.acquire()
        try:
            for group in self.groups:
                if group.id == groupId:
                    # Found it, return it
                    return group
            return None
        finally:
            self.lock.release()

    def getOrAddGroup(self, groupId):
        """ Gets or creates the group with the given id. """
        self.lock.acquire()
        try:
            # Search for the group with the given id
            for group in self.groups:
                if group.id == groupId:
                    # Found it, return it
                    return group
            # Create and add it
            group = Group(groupId)
            self.groups.append(group)
            return group
        finally:
            self.lock.release()


class Drone:
    """ Class that handles a drone. """

    def __init__(self):
        self.x = 0


class Group:
    """ Class that handles a group. """

    def __init__(self, id):
        self.id = id
        self.drones = []

    def addDrone(self, drone):
        self.drones.append(drone)

    def removeDrone(self, drone):
        self.drones.remove(drone)


##############################
# Globals (cough)
##############################
app = Flask(__name__)
groups = Groups()

##############################
# Route Definitions
##############################


@app.route("/")
def hello():
    return "Welcome to CrazyServ!"


@app.route("/api/<groupId>/status")
def status(groupId):
    global groups
    group = groups.getGroup(groupId)
    if group is None:
        abort(404, description="Group not found")
    return jsonify({"group": group.id})


@app.route("/api/<groupId>/<droneId>/connect")
def connect(groupId, droneId):
    global groups
    group = groups.getOrAddGroup(groupId)
    return jsonify({'group': group.id})


@app.route('/shutdown', methods=['GET'])
def shutdown():
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
    app.run(debug=True, port=port)

'''
# Base API
/api/<groupId>
 
# Take Off
/<droneId>/takeoff?z=<z>&v=<v>
# Response
Expected duration
 
# Land
/<droneId>/land?z=<z>&v=<v>
# Response
Expected duration
 
# Stop
/<droneId>/stop
 
# Go to
/<droneId>/goto?x=<x>&y=<y>&z=<z>&yaw=<yaw>&v=<v>
# Response
Expected duration
 
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
 
# Connect
/<droneId>/connect?group=<group>
# Response
Ok, Not ok, Not found
'''
