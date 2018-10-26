using System.Threading.Tasks;
using CrazyServLib.ApiObjects;

namespace CrazyServLib.Models
{
    public class Drone
    {
        public Drone(string id, Swarm swarm)
        {
            Id = id;
            Swarm = swarm;
        }

        /// <summary>
        /// The id of the drone.
        /// </summary>
        public string Id { get; }

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

        public async Task<TakeoffLandResult> Takeoff(double z, double velocity)
        {
            return await CrazyServApi.Takeoff(Swarm.Id, Id, z, velocity);
        }

        public async Task<TakeoffLandResult> Land(double z, double velocity)
        {
            return await CrazyServApi.Land(Swarm.Id, Id, z, velocity);
        }

        public async Task<GoToResult> GoTo(double x, double y, double z, double velocity, double yaw = 0, bool relative = false)
        {
            return await CrazyServApi.GoTo(Swarm.Id, Id, x, y, z, velocity, yaw, relative);
        }

        public async Task<SuccessResult> Calibrate()
        {
            return await CrazyServApi.Calibrate(Swarm.Id, Id);
        }

        public async Task<DroneStatus> Stop()
        {
            return await CrazyServApi.Stop(Swarm.Id, Id);
        }

        public async Task<DroneStatus> UpdateStatus()
        {
            var status = await CrazyServApi.DroneStatus(Swarm.Id, Id);
            UpdateFromStatus(status);
            return status;
        }

        internal void UpdateFromStatus(DroneStatus droneStatus)
        {
            X = droneStatus.X;
            Y = droneStatus.Y;
            Z = droneStatus.Z;
            BatteryPercentage = droneStatus.BatteryPercentage;
        }
    }
}
