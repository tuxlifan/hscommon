# Created By: Virgil Dupras
# Created On: 2007-06-17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging

from ..testcase import TestCase
from ..decorators import *

class LogCalls(TestCase):
    @log_calls
    def foobar(self, a, b):
        return a + b
    
    def foobaz(self, a, b):
        return a * b
    
    def with_defaults(self, a, b=42, c=12):
        return 42
    
    @log_calls
    def with_locals(self, a, b=2):
        foo = 'bleh'
        return foo
        
    def test_typical(self):
        self.assertEqual(42 + 23, self.foobar(42, 23))
        self.foobar(12, b=13)
        expected = [
            {'self': self, 'a': 42, 'b': 23},
            {'self': self, 'a': 12, 'b': 13},
        ]
        self.assertEqual(expected, self.foobar.calls)
    
    def test_builtin(self):
        # builtin functions don't have func_code.
        logged_max = log_calls(max)
        logged_max(12, 13)
        self.assertEqual(1, len(logged_max.calls))
    
    def test_bound_method(self):
        self.mock(self, 'foobaz', log_calls(self.foobaz))
        self.assertEqual(42 * 23, self.foobaz(42, 23))
        self.foobaz(12, b=13)
        expected = [
            {'self': self, 'a': 42, 'b': 23},
            {'self': self, 'a': 12, 'b': 13},
        ]
        self.assertEqual(expected, self.foobaz.calls)
    
    def test_log_defaults(self):
        self.mock(self, 'with_defaults', log_calls(self.with_defaults))
        self.with_defaults(58)
        self.with_defaults(58, 24)
        self.with_defaults(58, 24, 32)
        self.with_defaults(58, b=76)
        expected = [
            {'self': self, 'a': 58, 'b': 42, 'c': 12},
            {'self': self, 'a': 58, 'b': 24, 'c': 12},
            {'self': self, 'a': 58, 'b': 24, 'c': 32},
            {'self': self, 'a': 58, 'b': 76, 'c': 12},
        ]
        self.assertEqual(self.with_defaults.calls, expected)
    
    def test_log_calls_with_local_vars(self):
        """Variables in the local scope don't end up in the call dict"""
        self.with_locals(42, 24)
        call = self.with_locals.calls[0]
        expected = {'self': self, 'a': 42, 'b': 24}
        self.assertEqual(call, expected)
    

class PrintCalls(TestCase):
    @print_calls
    def foobar(self, a, b):
        return a + b
    
    @print_calls
    def foobaz(self, c, d):
        return c + d
    
    def setUp(self):
        self.mock(logging, 'info', log_calls(lambda msg: None))
    
    def test_typical(self):
        self.assertEqual(42 + 23, self.foobar(42, 23))
        msg = logging.info.calls[0]['msg']
        self.assert_('foobar' in msg)
        self.assert_('\'self\': ' in msg)
        self.assert_('\'a\': 42' in msg)
        self.assert_('\'b\': 23' in msg)
        self.foobaz(12, d=13)
        msg = logging.info.calls[2]['msg']
        self.assert_('foobaz' in msg)
        self.assert_('\'self\': ' in msg)
        self.assert_('\'c\': 12' in msg)
        self.assert_('\'d\': 13' in msg)
    
