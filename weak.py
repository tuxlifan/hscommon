# Created By: Virgil Dupras
# Created On: 2008-01-11
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81253 (modified (heavily))

# For some reason, methods don't play well with weakref, and need some kind of workaround
# that keep the weakref on the method's instance instead of the method itself.

from weakref import ref

class Dummy(object):
    def met(self):
        pass

instancemethod = type(Dummy.met) # we need to extract the type of an instance method

class WeakMethod:
    def __init__(self, method):
        self.func = method.im_func
        self.w_instance = ref(method.im_self)
    
    def __call__(self):
        instance = self.w_instance()
        if instance is not None:
            return instancemethod(self.func, instance, instance.__class__)
    

def methodref(method):
    try:
        return WeakMethod(method)
    except AttributeError: # It's not a method, we can return a normal weakref
        return ref(method)
