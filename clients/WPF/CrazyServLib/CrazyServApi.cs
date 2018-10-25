using System;
using System.Net.Http;
using System.Threading.Tasks;
using CrazyServLib.ApiObjects;
using Newtonsoft.Json;

namespace CrazyServLib
{
    public static class CrazyServApi
    {
        /// <summary>
        /// Base URL of the server like http://localhost:5000
        /// </summary>
        public static string BaseUrl { get; set; }

        public static async Task<DroneStatus> DroneStatus(string swarmId, string droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/status");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<DroneStatus>(value);
                return result;
            }
            return null;
        }

        public static async Task<Arena> Arena()
        {
            var client = GetClient();
            var resp = await client.GetAsync("/api/arena");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<Arena>(value);
                return result;
            }
            return null;
        }

        public static async Task<DroneStatus[]> SwarmStatus(string swarmId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/status");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<DroneStatus[]>(value);
                return result;
            }
            return null;
        }

        public static async Task<SuccessResult> Connect(string swarmId, string droneId, int radioId, int channel, string address, string dataRate)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/connect?r={radioId}&c={channel}&a={address}&dr={dataRate}");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<SuccessResult>(value);
                return result;
            }
            return null;
        }

        public static async Task<SuccessResult> Disconnect(string swarmId, string droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/disconnect");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<SuccessResult>(value);
                return result;
            }
            return null;
        }

        public static async Task<SuccessResult> Calibrate(string swarmId, string droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/calibrate");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<SuccessResult>(value);
                return result;
            }
            return null;
        }

        public static async Task<TakeoffLandResult> Takeoff(string swarmId, string droneId, double z, double v)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/takeoff?z={z}&v={v}");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<TakeoffLandResult>(value);
                return result;
            }
            return null;
        }

        public static async Task<TakeoffLandResult> Land(string swarmId, string droneId, double z, double v)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/land?z={z}&v={v}");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<TakeoffLandResult>(value);
                return result;
            }
            return null;
        }

        public static async Task<DroneStatus> Stop(string swarmId, string droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/stop");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<DroneStatus>(value);
                return result;
            }
            return null;
        }

        public static async Task<GoToResult> GoTo(string swarmId, string droneId, double x, double y, double z, double yaw, double velocity, bool relative = false)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/goto?x={x}&y={y}&z={z}&yaw={yaw}&v={velocity}&r={(relative ? 1 : 0)}");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var result = TryDeserialize<GoToResult>(value);
                return result;
            }
            return null;
        }

        private static HttpClient GetClient()
        {
            var client = new HttpClient { BaseAddress = new Uri(BaseUrl) };
            return client;
        }

        private static T TryDeserialize<T>(string json)
        {
            try
            {
                return JsonConvert.DeserializeObject<T>(json);
            }
            catch (Exception ex)
            {
                throw;
            }
        }
    }
}
