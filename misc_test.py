#!/usr/bin/env python
# Unit Name: hsutil.misc_test
# Created By: Virgil Dupras
# Created On: 2006/02/21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from .testcase import TestCase
from .misc import *

class TCFlags(TestCase):
    def testStrToFlags(self):
        self.assertEqual(StrToFlags('A'),(0,6))
        self.assertEqual(StrToFlags('A',4),(0,))
        self.assertEqual(StrToFlags('AB'),(1,6,8,14))
        self.assertEqual(StrToFlags('AB',8),(1,6))

    def testIntToFlags(self):
        self.assertEqual(IntToFlags(0xff,8),(0,1,2,3,4,5,6,7))
        self.assertEqual(IntToFlags(0x41,8),(0,6))
        self.assertEqual(IntToFlags(0x41424344),(2,6,8,9,14,17,22,24,30))
        self.assertEqual(IntToFlags(0x41424344,24),(2,6,8,9,14,17,22))
        self.assertEqual(IntToFlags(0),())

    def testFlagsToInt(self):
        self.assertEqual(FlagsToInt((0,1,2,3,4,5,6,7)), 0xff)
        self.assertEqual(FlagsToInt((0,6)), 0x41)
        self.assertEqual(FlagsToInt(IntToFlags(0x41424344)), 0x41424344)
        self.assertEqual(FlagsToInt(()),0)

class TCMisc(TestCase):
    def test_dedupe(self):
        reflist = [0,7,1,2,3,4,4,5,6,7,1,2,3]
        self.assertEqual(dedupe(reflist),[0,7,1,2,3,4,5,6])

    def test_flatten(self):
        self.assertEqual([1,2,3,4],flatten([[1,2],[3,4]]))
        self.assertEqual([],flatten([]))
    
    def test_flatten_startwith(self):
        start_with = [1,2]
        result = flatten([[3,4]],start_with)
        self.assertEqual([1,2,3,4],result)
        self.assert_(result is not start_with)
    
    def test_cond(self):
        self.assertEqual('foo',cond(True,'foo','bar'))
        self.assertEqual('bar',cond(False,'foo','bar'))
    
    def test_nonone(self):
        self.assertEqual('foo', nonone('foo', 'bar'))
        self.assertEqual('bar', nonone(None, 'bar'))
    
    def test_tryint(self):
        self.assertEqual(42,tryint('42'))
        self.assertEqual(0,tryint('abc'))
        self.assertEqual(0,tryint(None))
        self.assertEqual(42,tryint(None, 42))
    
    def test_stripnone(self):
        self.assertEqual([0, 1, 2, 3], stripnone([None, 0, 1, 2, 3, None]))
    
    def test_allsame(self):
        self.assertTrue(allsame([42, 42, 42]))
        self.assertFalse(allsame([42, 43, 42]))
        self.assertFalse(allsame([43, 42, 42]))
        # Works on non-sequence as well
        self.assertTrue(allsame(iter([42, 42, 42])))
        # Raises ValueError if fed an empty iterable
        self.assertRaises(ValueError, allsame, [])
    
    def test_first(self):
        self.assertEqual(first([3, 2, 1]), 3)
        self.assertEqual(first(i for i in [3, 2, 1] if i < 3), 2)
    
