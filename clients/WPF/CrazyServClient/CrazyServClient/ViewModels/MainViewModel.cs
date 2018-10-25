using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using CrazyServClient.Core;
using CrazyServLib;
using CrazyServLib.ApiObjects;

namespace CrazyServClient.ViewModels
{
    public class MainViewModel : ObservableObject
    {
        const double canvasReduction = 0.3;

        public ICommand GetSwarmStatusCommand { get; }
        public ICommand ConnectDroneCommand { get; }
        public ICommand DisconnectDroneCommand { get; }
        public ICommand TakeoffCommand { get; }
        public ICommand LandCommand { get; }
        public ICommand StopCommand { get; }

        public Arena Arena { get; private set; }

        public double CanvasWidth
        {
            get => GetValue<double>();
            set => SetValue(value);
        }

        public double CanvasHeight
        {
            get => GetValue<double>();
            set => SetValue(value);
        }

        public string BaseUrl
        {
            get => CrazyServApi.BaseUrl;
            set => CrazyServApi.BaseUrl = value;
        }

        public string SwarmName
        {
            get => GetValue<string>();
            set => SetValue(value);
        }

        public string DroneId
        {
            get => GetValue<string>();
            set => SetValue(value);
        }

        public ObservableCollection<CanvasItemViewModel> CanvasItems { get; } = new ObservableCollection<CanvasItemViewModel>();

        public MainViewModel()
        {
            GetSwarmStatusCommand = new RelayCommand(o =>
            {
                var drones = Task.Run(async () => await CrazyServApi.SwarmStatus(SwarmName)).Result;
                CanvasItems.Clear();
                var canvasXMin = CanvasWidth * canvasReduction;
                var canvasXMax = CanvasWidth * (1 - canvasReduction);
                var canvasYMin = CanvasHeight * canvasReduction;
                var canvasYMax = CanvasHeight * (1 - canvasReduction);
                CanvasItems.Add(new AnchorViewModel() { X = canvasXMin, Y = canvasYMin });
                CanvasItems.Add(new AnchorViewModel() { X = canvasXMin, Y = canvasYMax });
                CanvasItems.Add(new AnchorViewModel() { X = canvasXMax, Y = canvasYMax });
                CanvasItems.Add(new AnchorViewModel() { X = canvasXMax, Y = canvasYMin });
                foreach (var drone in drones)
                {
                    var droneVm = new DroneViewModel();
                    droneVm.Id = drone.Id;
                    droneVm.Battery = drone.BatteryPercentage;
                    droneVm.X = drone.X / (Arena.MaxX - Arena.MinX) * (canvasXMax - canvasXMin) + canvasXMin;
                    droneVm.Y = drone.Y / (Arena.MaxY - Arena.MinY) * (canvasYMax - canvasYMin) + canvasYMin;
                    CanvasItems.Add(droneVm);
                }
            });
            ConnectDroneCommand = new RelayCommand(o =>
            {
                CrazyServApi.ConnectDrone(SwarmName, Convert.ToInt32(DroneId));
            });
            DisconnectDroneCommand = new RelayCommand(o =>
            {
                CrazyServApi.DisconnectDrone(SwarmName, Convert.ToInt32(DroneId));
            });
            TakeoffCommand = new RelayCommand(o =>
            {
                CrazyServApi.Takeoff(SwarmName, Convert.ToInt32(DroneId), 1, 0.2);
            });
            LandCommand = new RelayCommand(o =>
            {
                CrazyServApi.Land(SwarmName, Convert.ToInt32(DroneId), 0, 0.2);
            });
            StopCommand = new RelayCommand(o =>
            {
                CrazyServApi.Stop(SwarmName, Convert.ToInt32(DroneId));
            });
        }

        public async Task InitArena()
        {
            Arena = await CrazyServApi.Arena();
        }

        public async Task SendDroneTo(Point targetPosition)
        {
            var canvasXMin = CanvasWidth * canvasReduction;
            var canvasXMax = CanvasWidth * (1 - canvasReduction);
            var canvasYMin = CanvasHeight * canvasReduction;
            var canvasYMax = CanvasHeight * (1 - canvasReduction);

            var newX = (targetPosition.X - canvasXMin) * (Arena.MaxX - Arena.MinX) / (canvasXMax - canvasXMin);
            var newY = (targetPosition.Y - canvasYMin) * (Arena.MaxY - Arena.MinY) / (canvasYMax - canvasYMin);

            Console.WriteLine($"Send drone to: {newX}/{newY}");
            CrazyServApi.GoTo(SwarmName, Convert.ToInt32(DroneId), newX, newY, 1, 0, 0.2);
        }
    }
}
