# Created By: Virgil Dupras
# Created On: 2008-01-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest

from ..conflict import *

class GetConflictedName(unittest.TestCase):
    def test_simple(self):
        name = get_conflicted_name(['bar'], 'bar')
        self.assertEqual('[000] bar', name)
        name = get_conflicted_name(['bar', '[000] bar'], 'bar')
        self.assertEqual('[001] bar', name)
    
    def test_no_conflict(self):
        name = get_conflicted_name(['bar'], 'foobar')
        self.assertEqual('foobar', name)
    
    def test_fourth_digit(self):
        """This test is long because every time we have to add a conflicted name,
        a test must be made for every other conflicted name existing...
        Anyway, this has very few chances to happen.
        """
        names = ['bar'] + ['[%03d] bar' % i for i in range(1000)]
        name = get_conflicted_name(names, 'bar')
        self.assertEqual('[1000] bar', name)
    
    def test_auto_unconflict(self):
        """Automatically unconflict the name if it's already conflicted.
        """
        name = get_conflicted_name([], '[000] foobar')
        self.assertEqual('foobar', name)
        name = get_conflicted_name(['bar'], '[001] bar')
        self.assertEqual('[000] bar', name)
    

class GetUnconflictedName(unittest.TestCase):
    def test_main(self):
        self.assertEqual('foobar',get_unconflicted_name('[000] foobar'))
        self.assertEqual('foobar',get_unconflicted_name('[9999] foobar'))
        self.assertEqual('[000]foobar',get_unconflicted_name('[000]foobar'))
        self.assertEqual('[000a] foobar',get_unconflicted_name('[000a] foobar'))
        self.assertEqual('foobar',get_unconflicted_name('foobar'))
        self.assertEqual('foo [000] bar',get_unconflicted_name('foo [000] bar'))
    

class IsConflicted(unittest.TestCase):
    def test_main(self):
        self.assertEqual(True,is_conflicted('[000] foobar'))
        self.assertEqual(True,is_conflicted('[9999] foobar'))
        self.assertEqual(False,is_conflicted('[000]foobar'))
        self.assertEqual(False,is_conflicted('[000a] foobar'))
        self.assertEqual(False,is_conflicted('foobar'))
        self.assertEqual(False,is_conflicted('foo [000] bar'))
    
