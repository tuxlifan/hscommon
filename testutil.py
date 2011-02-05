# Created By: Virgil Dupras
# Created On: 2010-11-14
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import datetime
import time
import py.path

def eq_(a, b, msg=None):
    __tracebackhide__ = True
    assert a == b, msg or "%r != %r" % (a, b)

def assert_almost_equal(a, b, places=7):
    __tracebackhide__ = True
    assert round(a, ndigits=places) == round(b, ndigits=places)

class TestData:
    def __init__(self, datadirpath):
        self.datadirpath = py.path.local(datadirpath)
    
    def filepath(self, relative_path, *args):
        """Returns the path of a file in testdata.
        
        'relative_path' can be anything that can be added to a Path
        if args is not empty, it will be joined to relative_path
        """
        resultpath = self.datadirpath.join(relative_path)
        if args:
            resultpath = resultpath.join(*args)
        assert resultpath.check()
        return str(resultpath)
    

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
        __tracebackhide__ = True
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
        __tracebackhide__ = True
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
    

# To use @with_app, you have to import pytest_funcarg__app in your conftest.py file.
def with_app(setupfunc):
    def decorator(func):
        func.setupfunc = setupfunc
        return func
    return decorator

def pytest_funcarg__app(request):
    setupfunc = request.function.setupfunc
    if hasattr(setupfunc, '__code__'):
        argnames = setupfunc.__code__.co_varnames[:setupfunc.__code__.co_argcount]
        def getarg(name):
            if name == 'self':
                return request.function.__self__
            else:
                return request.getfuncargvalue(name)
        args = [getarg(argname) for argname in argnames]
    else:
        args = []
    app = setupfunc(*args)
    return app

def patch_osstat(monkeypatch, path, st_mode=16877, st_ino=742635, st_dev=234881026, st_nlink=51,
    st_uid=501, st_gid=20, st_size=1734, st_atime=1257942648, st_mtime=1257873561, 
    st_ctime=1257873561):
    """ Patches os.stat for `path`.
    
    Patching os.stat can be tricky, because it can mess much more than what you're trying to test.
    Also, it can be cumbersome to do it. This method lets you do it easily. Just specify a path
    for which you want to patch os.stat, and specify the values through **kwargs. The defaults
    here are just some stats (that make sense) to fill up.
    
    Example call: patch_osstat(monkeypatch, Path('foo/bar'), st_mtime=42)
    """
    # This function is here temporarily. Evenutally, I'll make a pytest-monkeypatch-plus package
    if not hasattr(monkeypatch, '_patched_osstat'): # first osstat mock, actually install the mock
        monkeypatch._patched_osstat = {} # path: os.stat_result
        old_osstat = os.stat
        def fake_osstat(path_str):
            try:
                return monkeypatch._patched_osstat[path_str]
            except KeyError:
                return old_osstat(path_str)
        monkeypatch.setattr(os, 'stat', fake_osstat)
    st_seq = [st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime]
    monkeypatch._patched_osstat[str(path)] = os.stat_result(st_seq)

def patch_today(monkeypatch, year, month, day):
    """Patches today's date to date(year, month, day)
    """
    # For the patching to work system wide, time.time() must be patched. However, there is no way
    # to get a time.time() value out of a datetime, so a timedelta must be used
    new_today = datetime.date(year, month, day)
    today = datetime.date.today()
    time_now = time.time()
    delta = today - new_today
    monkeypatch.setattr(time, 'time', lambda: time_now - (delta.days * 24 * 60 * 60))

def _unify_args(func, args, kwargs, args_to_ignore=None):
    ''' Unify args and kwargs in the same dictionary.
    
        The result is kwargs with args added to it. func.func_code.co_varnames is used to determine
        under what key each elements of arg will be mapped in kwargs.
        
        if you want some arguments not to be in the results, supply a list of arg names in 
        args_to_ignore.
        
        if f is a function that takes *args, func_code.co_varnames is empty, so args will be put 
        under 'args' in kwargs.
        
        def foo(bar, baz)
        _unifyArgs(foo, (42,), {'baz': 23}) --> {'bar': 42, 'baz': 23}
        _unifyArgs(foo, (42,), {'baz': 23}, ['bar']) --> {'baz': 23}
    '''
    result = kwargs.copy()
    if hasattr(func, '__code__'): # built-in functions don't have func_code
        args = list(args)
        if getattr(func, '__self__', None) is not None: # bound method, we have to add self to args list
            args = [func.__self__] + args
        defaults = list(func.__defaults__) if func.__defaults__ is not None else []
        arg_count = func.__code__.co_argcount
        arg_names = list(func.__code__.co_varnames)
        if len(args) < arg_count: # We have default values
            required_arg_count = arg_count - len(args)
            args = args + defaults[-required_arg_count:]
        for arg_name, arg in zip(arg_names, args):
            # setdefault is used because if the arg is already in kwargs, we don't want to use default values
            result.setdefault(arg_name, arg)
    else:
        #'func' has a *args argument
        result['args'] = args
    if args_to_ignore:
        for kw in args_to_ignore:
            del result[kw]
    return result

def log_calls(func):
    ''' Logs all func calls' arguments under func.calls.
    
        func.calls is a list of _unify_args() result (dict).
        
        Mostly used for unit testing.
    '''
    def wrapper(*args, **kwargs):
        unifiedArgs = _unify_args(func, args, kwargs)
        wrapper.calls.append(unifiedArgs)
        return func(*args, **kwargs)
    
    wrapper.calls = []
    return wrapper
