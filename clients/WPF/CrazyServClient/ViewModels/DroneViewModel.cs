using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CrazyServClient.Core;

namespace CrazyServClient.ViewModels
{
    public class DroneViewModel : CanvasItemViewModel
    {
        public int Id
        {
            get => GetValue<int>();
            set => SetValue(value);
        }

        public double Battery
        {
            get => GetValue<double>();
            set => SetValue(value);
        }
    }
}
