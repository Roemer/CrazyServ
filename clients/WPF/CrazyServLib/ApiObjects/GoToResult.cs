using Newtonsoft.Json;

namespace CrazyServLib.ApiObjects
{
    public class GoToResult
    {
        [JsonProperty("duration")]
        public double Duration { get; set; }

        [JsonProperty("target_x")]
        public double TargetX { get; set; }

        [JsonProperty("target_y")]
        public double TargetY { get; set; }

        [JsonProperty("target_z")]
        public double TargetZ { get; set; }

        [JsonProperty("target_yaw")]
        public double TargetYaw { get; set; }

        [JsonProperty("relative")]
        public bool Relative { get; set; }
    }
}
