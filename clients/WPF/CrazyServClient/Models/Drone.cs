using System.Threading.Tasks;
using CrazyServLib;
using CrazyServLib.ApiObjects;

namespace CrazyServClient.Models
{
    public class Drone
    {
        public Drone(Swarm swarm)
        {
            Swarm = swarm;
        }

        /// <summary>
        /// The id of the drone.
        /// </summary>
        public string Id { get; set; }

        /// <summary>
        /// The swarm that the drone belongs to.
        /// </summary>
        public Swarm Swarm { get; }

        /// <summary>
        /// The current X position of the drone.
        /// </summary>
        public double X { get; private set; }

        /// <summary>
        /// The current y position of the drone.
        /// </summary>
        public double Y { get; private set; }

        /// <summary>
        /// The current z position of the drone.
        /// </summary>
        public double Z { get; private set; }

        /// <summary>
        /// The current percentage of the state of the battery.
        /// </summary>
        public double BatteryPercentage { get; private set; }

        public void Takeoff(double z, double velocity)
        {
            CrazyServApi.Takeoff(Swarm.Id, Id, z, velocity);
        }

        public void Land(double z, double velocity)
        {
            CrazyServApi.Land(Swarm.Id, Id, z, velocity);
        }

        public void GoTo(double x, double y, double z, double velocity, double yaw = 0, bool relative = false)
        {
            CrazyServApi.GoTo(Swarm.Id, Id, x, y, z, velocity, yaw, relative);
        }

        public void Stop()
        {
            CrazyServApi.Stop(Swarm.Id, Id);
        }

        public async Task<DroneStatus> UpdateStatus()
        {
            var status = await CrazyServApi.DroneStatus(Swarm.Id, Id);
            X = status.X;
            Y = status.Y;
            Z = status.Z;
            BatteryPercentage = status.BatteryPercentage;
            return status;
        }
    }
}
