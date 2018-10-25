using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Input;

namespace CrazyServClient.Core
{
    public class AsyncRelayCommand : ICommand
    {
        private readonly Func<object, Task> _methodToExecute;
        private readonly Func<object, bool> _canExecuteEvaluator;

        private long _isExecuting;

        public AsyncRelayCommand(Func<object, Task> methodToExecute, Func<object, bool> canExecute = null)
        {
            _methodToExecute = methodToExecute;
            _canExecuteEvaluator = canExecute ?? (o => true);
        }

        public event EventHandler CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }

        public void RaiseCanExecuteChanged()
        {
            CommandManager.InvalidateRequerySuggested();
        }

        [DebuggerStepThrough]
        public bool CanExecute(object parameter)
        {
            if (Interlocked.Read(ref _isExecuting) != 0)
            {
                return false;
            }

            return _canExecuteEvaluator(parameter);
        }

        public async void Execute(object parameter)
        {
            Interlocked.Exchange(ref _isExecuting, 1);
            RaiseCanExecuteChanged();

            try
            {
                await _methodToExecute(parameter);
            }
            finally
            {
                Interlocked.Exchange(ref _isExecuting, 0);
                RaiseCanExecuteChanged();
            }
        }
    }
}
