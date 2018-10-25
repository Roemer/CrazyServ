using CrazyServClient.Core;

namespace CrazyServClient.ViewModels
{
    public abstract class CanvasItemViewModel : ObservableObject
    {
        public double X
        {
            get => GetValue<double>();
            set => SetValue(value);
        }

        public double Y
        {
            get => GetValue<double>();
            set => SetValue(value);
        }
    }
}
