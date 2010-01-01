# Created By: Virgil Dupras
# Created On: 2008-01-11
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

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

