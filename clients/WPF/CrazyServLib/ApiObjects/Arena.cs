using Newtonsoft.Json;

namespace CrazyServLib.ApiObjects
{
    public class Arena
    {
        [JsonProperty("min_x")]
        public double MinX { get; set; }

        [JsonProperty("max_x")]
        public double MaxX { get; set; }

        [JsonProperty("min_y")]
        public double MinY { get; set; }

        [JsonProperty("max_y")]
        public double MaxY { get; set; }

        [JsonProperty("min_z")]
        public double MinZ { get; set; }

        [JsonProperty("max_z")]
        public double MaxZ { get; set; }
    }
}
