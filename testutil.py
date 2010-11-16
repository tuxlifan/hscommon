# Created By: Virgil Dupras
# Created On: 2010-11-14
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hsutil.testutil import eq_

class CallLogger:
    """This is a dummy object that logs all calls made to it.
    
    It is used to simulate the GUI layer.
    """
    def __init__(self):
        self.calls = []
    
    def __getattr__(self, func_name):
        def func(*args, **kw):
            self.calls.append(func_name)
        return func
    
    def clear_calls(self):
        del self.calls[:]
    
    def check_gui_calls(self, expected, verify_order=False):
        """Checks that the expected calls have been made to 'self', then clears the log.
        
        `expected` is an iterable of strings representing method names.
        If `verify_order` is True, the order of the calls matters.
        """
        if verify_order:
            eq_(self.calls, expected)
        else:
            eq_(set(self.calls), set(expected))
        self.clear_calls()
    
    def check_gui_calls_partial(self, expected=None, not_expected=None, verify_order=False):
        """Checks that the expected calls have been made to 'self', then clears the log.
        
        `expected` is an iterable of strings representing method names. Order doesn't matter.
        Moreover, if calls have been made that are not in expected, no failure occur.
        `not_expected` can be used for a more explicit check (rather than calling `check_gui_calls`
        with an empty `expected`) to assert that calls have *not* been made.
        """
        if expected is not None:
            not_called = set(expected) - set(self.calls)
            assert not not_called, "These calls haven't been made: {0}".format(not_called)
            if verify_order:
                max_index = 0
                for call in expected:
                    index = self.calls.index(call)
                    if index < max_index:
                        raise AssertionError("The call {0} hasn't been made in the correct order".format(call))
                    max_index = index
        if not_expected is not None:
            called = set(not_expected) & set(self.calls)
            assert not called, "These calls shouldn't have been made: {0}".format(called)
        self.clear_calls()
    

class TestApp:
    def clear_gui_calls(self):
        for attr in dir(self):
            if attr.endswith('_gui'):
                gui = getattr(self, attr)
                if hasattr(gui, 'calls'): # We might have test methods ending with '_gui'
                    gui.clear_calls()
    
    def make_gui(self, name, class_, view=None, parent=None, holder=None):
        if view is None:
            view = CallLogger()
        if parent is None:
            parent = self.mw
        if holder is None:
            holder = self
        setattr(holder, '{0}_gui'.format(name), view)
        gui = class_(view, parent)
        setattr(holder, name, gui)
        return gui
    

def with_app(appfunc):
    # This decorator sends the app resulting from the `appfunc` call as an argument to the decorated
    # `func`. `appfunc` must return a TestApp instance. Additionally, `appfunc` can also return a
    # tuple (app, patcher). In this case, the patcher will perform unpatching after having called
    # the decorated func.
    def decorator(func):
        def wrapper(): # a test is not supposed to take args
            appresult = appfunc()
            if isinstance(appresult, tuple):
                app, patcher = appresult
            else:
                app = appresult
                patcher = None
            assert isinstance(app, TestApp)
            try:
                func(app)
            finally:
                if patcher is not None:
                    patcher.unpatch()
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator
