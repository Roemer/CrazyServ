using System;

namespace CrazyServClient.Core
{
    public class RelayCommand : TypedRelayCommand<object>
    {
        public RelayCommand(Action<object> methodToExecute, Func<object, bool> canExecuteEvaluator = null)
            : base(methodToExecute, canExecuteEvaluator)
        {
        }
    }
}
