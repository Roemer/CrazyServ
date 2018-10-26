using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using CrazyServClient.Core;
using CrazyServLib;
using CrazyServLib.ApiObjects;
using Arena = CrazyServLib.Models.Arena;

namespace CrazyServClient.ViewModels
{
    public class MainViewModel : ObservableObject
    {
        const double CanvasReduction = 0.3;

        public ICommand GetSwarmStatusCommand { get; }
        public ICommand ConnectDroneCommand { get; }
        public ICommand DisconnectDroneCommand { get; }
        public ICommand TakeoffCommand { get; }
        public ICommand LandCommand { get; }
        public ICommand StopCommand { get; }

        public Arena Arena { get; } = new Arena();

        public string StatusBarText
        {
            get => GetValue<string>();
            set => SetValue(value);
        }

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

        public string RadioId
        {
            get => GetValue<string>();
            set => SetValue(value);
        }

        public string Channel
        {
            get => GetValue<string>();
            set => SetValue(value);
        }

        public string Address
        {
            get => GetValue<string>();
            set => SetValue(value);
        }

        public string DataRate
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
                var canvasXMin = CanvasWidth * CanvasReduction;
                var canvasXMax = CanvasWidth * (1 - CanvasReduction);
                var canvasYMin = CanvasHeight * CanvasReduction;
                var canvasYMax = CanvasHeight * (1 - CanvasReduction);
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
                CrazyServApi.Connect(SwarmName, DroneId, Convert.ToInt32(RadioId), Convert.ToInt32(Channel), Address, DataRate);
            });
            DisconnectDroneCommand = new RelayCommand(o =>
            {
                CrazyServApi.Disconnect(SwarmName, DroneId);
            });
            TakeoffCommand = new RelayCommand(o =>
            {
                CrazyServApi.Takeoff(SwarmName, DroneId, 1, 0.2);
            });
            LandCommand = new RelayCommand(o =>
            {
                CrazyServApi.Land(SwarmName, DroneId, 0, 0.2);
            });
            StopCommand = new RelayCommand(o =>
            {
                CrazyServApi.Stop(SwarmName, DroneId);
            });
        }

        public async Task<GoToResult> SendDroneTo(Point targetPosition)
        {
            var canvasXMin = CanvasWidth * CanvasReduction;
            var canvasXMax = CanvasWidth * (1 - CanvasReduction);
            var canvasYMin = CanvasHeight * CanvasReduction;
            var canvasYMax = CanvasHeight * (1 - CanvasReduction);

            var newX = (targetPosition.X - canvasXMin) * (Arena.MaxX - Arena.MinX) / (canvasXMax - canvasXMin);
            var newY = (targetPosition.Y - canvasYMin) * (Arena.MaxY - Arena.MinY) / (canvasYMax - canvasYMin);

            Console.WriteLine($"Send drone to: {newX}/{newY}");
            return await CrazyServApi.GoTo(SwarmName, DroneId, newX, newY, 1, 0, 0.2);
        }
    }
}
