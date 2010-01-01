# Created By: Virgil Dupras
# Created On: 2006/02/21
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from nose.tools import eq_, raises

from ..testcase import TestCase
from ..misc import *

def testStrToFlags():
    eq_(StrToFlags('A'),(0,6))
    eq_(StrToFlags('A',4),(0,))
    eq_(StrToFlags('AB'),(1,6,8,14))
    eq_(StrToFlags('AB',8),(1,6))

def testIntToFlags():
    eq_(IntToFlags(0xff,8),(0,1,2,3,4,5,6,7))
    eq_(IntToFlags(0x41,8),(0,6))
    eq_(IntToFlags(0x41424344),(2,6,8,9,14,17,22,24,30))
    eq_(IntToFlags(0x41424344,24),(2,6,8,9,14,17,22))
    eq_(IntToFlags(0),())

def testFlagsToInt():
    eq_(FlagsToInt((0,1,2,3,4,5,6,7)), 0xff)
    eq_(FlagsToInt((0,6)), 0x41)
    eq_(FlagsToInt(IntToFlags(0x41424344)), 0x41424344)
    eq_(FlagsToInt(()),0)

def test_dedupe():
    reflist = [0,7,1,2,3,4,4,5,6,7,1,2,3]
    eq_(dedupe(reflist),[0,7,1,2,3,4,5,6])

def test_flatten():
    eq_([1,2,3,4],flatten([[1,2],[3,4]]))
    eq_([],flatten([]))

def test_flatten_startwith():
    start_with = [1,2]
    result = flatten([[3,4]],start_with)
    eq_([1,2,3,4],result)
    assert result is not start_with

def test_cond():
    eq_('foo',cond(True,'foo','bar'))
    eq_('bar',cond(False,'foo','bar'))

def test_nonone():
    eq_('foo', nonone('foo', 'bar'))
    eq_('bar', nonone(None, 'bar'))

def test_tryint():
    eq_(42,tryint('42'))
    eq_(0,tryint('abc'))
    eq_(0,tryint(None))
    eq_(42,tryint(None, 42))

def test_stripnone():
    eq_([0, 1, 2, 3], stripnone([None, 0, 1, 2, 3, None]))

def test_allsame():
    assert allsame([42, 42, 42])
    assert not allsame([42, 43, 42])
    assert not allsame([43, 42, 42])
    # Works on non-sequence as well
    assert allsame(iter([42, 42, 42]))

@raises(ValueError)
def test_allsame_empty_arg():
    # Raises ValueError if fed an empty iterable
    allsame([])

def test_first():
    eq_(first([3, 2, 1]), 3)
    eq_(first(i for i in [3, 2, 1] if i < 3), 2)

def test_extract():
    wheat, shaft = extract(lambda n: n % 2 == 0, range(10))
    eq_(wheat, [0, 2, 4, 6, 8])
    eq_(shaft, [1, 3, 5, 7, 9])