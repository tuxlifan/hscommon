#!/usr/bin/env python
# Unit Name: hsutil.weak_test
# Created By: Virgil Dupras
# Created On: 2008-01-11
# $Id$
# Copyright 2008 Hardcoded Software (http://www.hardcoded.net)

import unittest

from .weak import methodref

class WeakMethod(unittest.TestCase):
    def test_method(self):
        class Dummy(object):
            def method(self):
                return 42

        d = Dummy()
        w = methodref(d.method)
        self.assertEqual(w(), d.method)
        self.assertEqual(w()(), 42)
        del d
        self.assert_(w() is None)
    
    def test_function(self):
        def function():
            return 54
        w = methodref(function)
        self.assertEqual(w(), function)
        self.assertEqual(w()(), 54)
        del function
        self.assert_(w() is None)
    
