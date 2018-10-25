using Newtonsoft.Json;

namespace CrazyServLib.ApiObjects
{
    public class SuccessResult
    {
        [JsonProperty("success")]
        public bool Success { get; set; }
    }
}
