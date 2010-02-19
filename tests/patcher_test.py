# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-19
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from nose.tools import eq_

from ..patcher import Patcher

class TestObj(object):
    attr1 = 'value1'
    attr2 = 'value2'

def test_patch_sets_attribute():
    p = Patcher()
    o = TestObj()
    p.patch(o, 'attr1', 'othervalue')
    eq_(o.attr1, 'othervalue')

def test_patch_puts_old_attr_back_at_unpatch():
    p = Patcher()
    o = TestObj()
    p.patch(o, 'attr1', 'mock1')
    p.patch(o, 'attr2', 'mock2')
    eq_(o.attr1, 'mock1')
    eq_(o.attr2, 'mock2')
    p.unpatch()
    eq_(o.attr1, 'value1')
    eq_(o.attr2, 'value2')

def test_mock_today():
    # mocking today is cumbersome and this is a shortcut
    p = Patcher()
    real_today = date.today()
    p.patch_today(2008, 3, 4)
    eq_(date.today(), date(2008, 3, 4))
    p.unpatch()
    eq_(date.today(), real_today)

def test_mock_twice():
    # When the same value is mocked twice, we want the original value to be put back
    p = Patcher()
    o = TestObj()
    p.patch(o, 'attr1', 'mock1')
    p.patch(o, 'attr1', 'mock2')
    eq_(o.attr1, 'mock2')
    p.unpatch()
    eq_(o.attr1, 'value1')

def test_mock_automatically_mocks_from_imports():
    # when `target_module` has an instance of the patched object (because it made a "from" import),
    # this instance is patched as well. Note that this test is a little bit flaky because it needs
    # a module that does a from import. So this test depends on the import scheme of path.
    from .. import path
    import itertools
    real_izip = itertools.izip
    p = Patcher(target_module=path)
    p.patch(itertools, 'izip', 'foobar')
    eq_(path.izip, 'foobar')
    p.unpatch()
    assert path.izip is real_izip
