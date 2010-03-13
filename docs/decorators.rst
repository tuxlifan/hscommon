============================================
:mod:`decorators` - Useful little decorators
============================================

.. function:: log_calls(func)

    Logs all func calls' arguments under func.calls. func.calls is a list of _unify_args() result (dict). Mostly used for unit testing.

.. function:: print_calls(func)

    Logs func name and all func calls' arguments with logging.info(). Mostly used for debugging. the name @log_calls was already taken...
