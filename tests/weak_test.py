# Unit Name: hsutil.tests.weak_test
# Created By: Virgil Dupras
# Created On: 2008-01-11
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from nose.tools import eq_

from ..weak import methodref

def test_method():
    class Dummy(object):
        def method(self):
            return 42

    d = Dummy()
    w = methodref(d.method)
    eq_(w(), d.method)
    eq_(w()(), 42)
    del d
    assert w() is None

def test_function():
    def function():
        return 54
    
    w = methodref(function)
    eq_(w(), function)
    eq_(w()(), 54)
    del function
    assert w() is None

