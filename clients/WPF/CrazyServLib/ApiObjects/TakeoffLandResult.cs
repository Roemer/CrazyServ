using Newtonsoft.Json;

namespace CrazyServLib.ApiObjects
{
    public class TakeoffLandResult
    {
        [JsonProperty("duration")]
        public float Duration { get; set; }

        [JsonProperty("target_z")]
        public float TargetZ { get; set; }
    }
}
