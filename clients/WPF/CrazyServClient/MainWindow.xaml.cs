using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using CrazyServClient.ViewModels;

namespace CrazyServClient
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private readonly MainViewModel _viewModel = new MainViewModel();

        public MainWindow()
        {
            InitializeComponent();

            _viewModel.BaseUrl = "http://nb50224:5000/";
            _viewModel.SwarmName = "rbl";
            _viewModel.DroneId = "MyDrone";
            _viewModel.RadioId = "0";
            _viewModel.Channel = "80";
            _viewModel.Address = "E7E7E7E7E7";
            _viewModel.DataRate = "2M";

            Task.Run(() => _viewModel.InitArena()).Wait();

            DataContext = _viewModel;
        }

        private void Ic_OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            _viewModel.CanvasWidth = e.NewSize.Width;
            _viewModel.CanvasHeight = e.NewSize.Height;
        }

        private void UIElement_OnMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            _viewModel.SendDroneTo(e.GetPosition(sender as IInputElement));
        }
    }
}
