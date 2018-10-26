using System.Collections.Generic;
using System.Threading.Tasks;
using CrazyServLib.ApiObjects;

namespace CrazyServLib.Models
{
    public class Swarm
    {
        public Swarm(string id)
        {
            Id = id;
            Drones = new Dictionary<string, Drone>();
        }

        public string Id { get; }

        public Dictionary<string, Drone> Drones { get; }

        public async Task<DroneStatus[]> UpdateStatus()
        {
            var status = await CrazyServApi.SwarmStatus(Id);
            foreach (var droneStatus in status)
            {
                if (Drones.ContainsKey(droneStatus.Id))
                {
                    var drone = Drones[droneStatus.Id];
                    drone.UpdateFromStatus(droneStatus);
                }
                else
                {
                    var drone = new Drone(droneStatus.Id, this);
                    drone.UpdateFromStatus(droneStatus);
                }
            }
            return status;
        }
    }
}
