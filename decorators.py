#!/usr/bin/env python
# Unit Name: hsutil.decorators
# Created By: Virgil Dupras
# Created On: 2007-06-17
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import logging

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
    if hasattr(func, 'func_code'): # built-in functions don't have func_code
        args = list(args)
        if getattr(func, 'im_self', None) is not None: # bound method, we have to add self to args list
            args = [func.im_self] + args
        defaults = list(func.func_defaults) if func.func_defaults is not None else []
        arg_count = func.func_code.co_argcount
        arg_names = list(func.func_code.co_varnames)
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

def print_calls(func):
    ''' Logs func name and all func calls' arguments with logging.info().
    
        Mostly used for debugging. the name @log_calls was already taken...
    '''
    def wrapper(*args, **kwargs):
        unified_args = _unify_args(func, args, kwargs)
        logging.info('Called %s() with args %r' % (func.func_name, unified_args))
        result = func(*args, **kwargs)
        logging.info('%s returning %r' % (func.func_name, result))
        return result
    
    return wrapper
