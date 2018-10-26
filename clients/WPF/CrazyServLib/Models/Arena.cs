using System.Threading.Tasks;

namespace CrazyServLib.Models
{
    public class Arena
    {
        public double MinX { get; private set; }

        public double MaxX { get; private set; }

        public double MinY { get; private set; }

        public double MaxY { get; private set; }

        public double MinZ { get; private set; }

        public double MaxZ { get; private set; }

        public async Task<ApiObjects.Arena> Update()
        {
            var arenaResponse = await CrazyServApi.Arena();
            MinX = arenaResponse.MinX;
            MaxX = arenaResponse.MaxX;
            MinY = arenaResponse.MinY;
            MaxY = arenaResponse.MaxY;
            MinZ = arenaResponse.MinZ;
            MaxZ = arenaResponse.MaxZ;
            return arenaResponse;
        }
    }
}
