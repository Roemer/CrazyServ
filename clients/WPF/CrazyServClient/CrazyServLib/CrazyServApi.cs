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



        public static async void DroneStatus(string swarmId, int droneId)
        {

        }

        public static async Task<Arena> Arena()
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/arena");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var arena = TryDeserialize<Arena>(value);
                return arena;
            }

            return null;
        }

        public static async Task<Drone[]> SwarmStatus(string swarmId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/status");
            if (resp.IsSuccessStatusCode)
            {
                var value = await resp.Content.ReadAsStringAsync();
                var swarm = TryDeserialize<Drone[]>(value);
                return swarm;
            }

            return null;
        }

        public static async void ConnectDrone(string swarmId, int droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/connect");
            var value = await resp.Content.ReadAsStringAsync();
        }

        public static async void DisconnectDrone(string swarmId, int droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/disconnect");
            var value = await resp.Content.ReadAsStringAsync();
        }

        public static async void Takeoff(string swarmId, int droneId, double z, double v)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/takeoff?z={z}&v={v}");
            var value = await resp.Content.ReadAsStringAsync();
        }

        public static async void Land(string swarmId, int droneId, double z, double v)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/land?z={z}&v={v}");
            var value = await resp.Content.ReadAsStringAsync();
        }

        public static async void Stop(string swarmId, int droneId)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/stop");
            var value = await resp.Content.ReadAsStringAsync();
        }

        public static async void GoTo(string swarmId, int droneId, double x, double y, double z, double yaw, double v)
        {
            var client = GetClient();
            var resp = await client.GetAsync($"/api/{swarmId}/{droneId}/goto?x={x}&y={y}&z={z}&yaw={yaw}&v={v}");
            var value = await resp.Content.ReadAsStringAsync();
        }

        public static HttpClient GetClient()
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
