#!/usr/bin/env python
"""
Unit Name: hs.markable_test
Created By: Virgil Dupras
Created On: 2006/02/23
Last modified by:$Author: virgil $
Last modified on:$Date: $
                 $Revision: $
Copyright 2004-2006 Hardcoded Software (http://www.hardcoded.net)
"""
import unittest
from .markable import *

class TCMarkable(unittest.TestCase):
    def gen(self):
        ml = MarkableList()
        ml.extend(range(10))
        return ml

    def test_unmarked(self):
        ml = self.gen()
        for i in ml:
            self.assert_(not ml.is_marked(i))

    def test_mark(self):
        ml = self.gen()
        self.assert_(ml.mark(3))
        self.assert_(ml.is_marked(3))
        self.assert_(not ml.is_marked(2))

    def test_unmark(self):
        ml = self.gen()
        ml.mark(4)
        self.assert_(ml.unmark(4))
        self.assert_(not ml.is_marked(4))

    def test_unmark_unmarked(self):
        ml = self.gen()
        self.assert_(not ml.unmark(4))
        self.assert_(not ml.is_marked(4))
        
    def test_mark_twice_and_unmark(self):
        ml = self.gen()
        self.assert_(ml.mark(5))
        self.assert_(not ml.mark(5))
        ml.unmark(5)
        self.assert_(not ml.is_marked(5))

    def test_mark_toggle(self):
        ml = self.gen()
        ml.mark_toggle(6)
        self.assert_(ml.is_marked(6))
        ml.mark_toggle(6)
        self.assert_(not ml.is_marked(6))
        ml.mark_toggle(6)
        self.assert_(ml.is_marked(6))

    def test_is_markable(self):
        class Foobar(Markable):
            def _is_markable(self, o):
                return o == 'foobar'
        f = Foobar()
        self.assert_(not f.is_marked('foobar'))
        self.assert_(not f.mark('foo'))
        self.assert_(not f.is_marked('foo'))
        f.mark_toggle('foo')
        self.assert_(not f.is_marked('foo'))
        f.mark('foobar')
        self.assert_(f.is_marked('foobar'))
        ml = self.gen()
        ml.mark(11)
        self.assert_(not ml.is_marked(11))

    def test_change_notifications(self):
        class Foobar(Markable):
            def _did_mark(self, o):
                self.log.append((True, o))
            def _did_unmark(self, o):
                self.log.append((False, o))

        f = Foobar()
        f.log = []
        f.mark('foo')
        f.mark('foo')
        f.mark_toggle('bar')
        f.unmark('foo')
        f.unmark('foo')
        f.mark_toggle('bar')
        self.assertEqual([(True,'foo'),(True,'bar'),(False,'foo'),(False,'bar')],f.log)

    def test_mark_count(self):
        ml = self.gen()
        self.assertEqual(0,ml.mark_count)
        ml.mark(7)
        self.assertEqual(1,ml.mark_count)
        ml.mark(11)
        self.assertEqual(1,ml.mark_count)

    def test_mark_none(self):
        log = []
        ml = self.gen()
        ml._did_unmark = lambda o: log.append(o)
        ml.mark(1)
        ml.mark(2)
        self.assertEqual(2,ml.mark_count)
        ml.mark_none()
        self.assertEqual(0,ml.mark_count)
        self.assertEqual([1,2],log)

    def test_mark_all(self):
        ml = self.gen()
        self.assertEqual(0,ml.mark_count)
        ml.mark_all()
        self.assertEqual(10,ml.mark_count)
        self.assert_(ml.is_marked(1))

    def test_mark_invert(self):
        ml = self.gen()
        ml.mark(1)
        ml.mark_invert()
        self.assert_(not ml.is_marked(1))
        self.assert_(ml.is_marked(2))

    def test_mark_while_inverted(self):
        log = []
        ml = self.gen()
        ml._did_unmark = lambda o:log.append((False,o))
        ml._did_mark = lambda o:log.append((True,o))
        ml.mark(1)
        ml.mark_invert()
        self.assert_(ml.mark_inverted)
        self.assert_(ml.mark(1))
        self.assert_(ml.unmark(2))
        self.assert_(ml.unmark(1))
        ml.mark_toggle(3)
        self.assert_(not ml.is_marked(3))
        self.assertEqual(7,ml.mark_count)
        self.assertEqual([(True,1),(False,1),(True,2),(True,1),(True,3)],log)
        
    def test_remove_mark_flag(self):
        ml = self.gen()
        ml.mark(1)
        ml._remove_mark_flag(1)
        self.assert_(not ml.is_marked(1))
        ml.mark(1)
        ml.mark_invert()
        self.assert_(not ml.is_marked(1))
        ml._remove_mark_flag(1)
        self.assert_(ml.is_marked(1))
        
    def test_is_marked_returns_false_if_object_not_markable(self):
        class MyMarkableList(MarkableList):
            def _is_markable(self, o):
                return o != 4
        ml = MyMarkableList()
        ml.extend(range(10))
        ml.mark_invert()
        self.assert_(ml.is_marked(1))
        self.assert_(not ml.is_marked(4))

if __name__ == "__main__":
    unittest.main()
