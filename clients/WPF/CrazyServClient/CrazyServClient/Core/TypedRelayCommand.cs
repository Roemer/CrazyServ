using System;
using System.Diagnostics;
using System.Windows.Input;

namespace CrazyServClient.Core
{
    public class TypedRelayCommand<T> : ICommand
    {
        private readonly Action<T> _methodToExecute;
        readonly Func<T, bool> _canExecuteEvaluator;

        public TypedRelayCommand(Action<T> methodToExecute, Func<T, bool> canExecuteEvaluator = null)
        {
            _methodToExecute = methodToExecute;
            _canExecuteEvaluator = canExecuteEvaluator;
        }

        [DebuggerStepThrough]
        public bool CanExecute(object parameter)
        {
            return _canExecuteEvaluator == null || _canExecuteEvaluator.Invoke((T)parameter);
        }

        public event EventHandler CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }

        public void Execute(object parameter)
        {
            _methodToExecute.Invoke((T)parameter);
        }
    }
}
