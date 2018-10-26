using Newtonsoft.Json;

namespace CrazyServLib.ApiObjects
{
    public class DroneStatus
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("var_x")]
        public double VarX { get; set; }

        [JsonProperty("var_y")]
        public double VarY { get; set; }

        [JsonProperty("var_z")]
        public double VarZ { get; set; }

        [JsonProperty("x")]
        public double X { get; set; }

        [JsonProperty("y")]
        public double Y { get; set; }

        [JsonProperty("z")]
        public double Z { get; set; }

        [JsonProperty("yaw")]
        public double Yaw { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("battery_voltage")]
        public double BatteryVoltage { get; set; }

        [JsonProperty("battery_percentage")]
        public double BatteryPercentage { get; set; }        
    }
}
