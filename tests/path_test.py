# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest
import sys

from nose.tools import assert_raises, eq_

from ..path import *
from ..testcase import TestCase

class TCPath(TestCase):
    def setUp(self):
        self.mock(os, 'sep', '/')
    
    def test_empty(self):
        path = Path('')
        eq_('',str(path))
        eq_(0,len(path))
        path = Path(())
        eq_('',str(path))
        eq_(0,len(path))
    
    def test_single(self):
        path = Path('foobar')
        eq_('foobar',path)
        eq_(1,len(path))
    
    def test_multiple(self):
        path = Path('foo/bar')
        eq_('foo/bar',path)
        eq_(2,len(path))
    
    def test_init_with_tuple_and_list(self):
        path = Path(('foo','bar'))
        eq_('foo/bar',path)
        path = Path(['foo','bar'])
        eq_('foo/bar',path)
    
    def test_init_with_invalid_value(self):
        try:
            path = Path(42)
            self.fail()
        except TypeError:
            pass
    
    def test_access(self):
        path = Path('foo/bar/bleh')
        eq_('foo',path[0])
        eq_('foo',path[-3])
        eq_('bar',path[1])
        eq_('bar',path[-2])
        eq_('bleh',path[2])
        eq_('bleh',path[-1])
    
    def test_slicing(self):
        path = Path('foo/bar/bleh')
        subpath = path[:2]
        eq_('foo/bar',subpath)
        self.assert_(isinstance(subpath,Path))
    
    def test_deal_with_empty_components(self):
        """Keep ONLY a leading space, which means we want a leading slash.
        """
        eq_('foo//bar',str(Path(('foo','','bar'))))
        eq_('/foo/bar',str(Path(('','foo','bar'))))
        eq_('foo/bar',str(Path('foo/bar/')))

    def test_old_compare_paths(self):
        eq_(Path('foobar'),Path('foobar'))
        eq_(Path('foobar/'),Path('foobar\\','\\'))
        eq_(Path('/foobar/'),Path('\\foobar\\','\\'))
        eq_(Path('/foo/bar'),Path('\\foo\\bar','\\'))
        eq_(Path('/foo/bar'),Path('\\foo\\bar\\','\\'))
        self.assertNotEqual(Path('/foo/bar'),Path('\\foo\\foo','\\'))
        #We also have to test __ne__
        self.assert_(not (Path('foobar') != Path('foobar')))
        self.assert_(Path('/a/b/c.x') != Path('/a/b/c.y'))
    
    def test_old_split_path(self):
        eq_(Path('foobar'),('foobar',))
        eq_(Path('foo/bar'),('foo','bar'))
        eq_(Path('/foo/bar/'),('','foo','bar'))
        eq_(Path('\\foo\\bar','\\'),('','foo','bar'))
    
    def test_representation(self):
        eq_("('foo', 'bar')",repr(Path(('foo','bar'))))
    
    def test_add(self):
        eq_('foo/bar/bar/foo',Path(('foo','bar')) + Path('bar/foo'))
        eq_('foo/bar/bar/foo',Path('foo/bar') + 'bar/foo')
        eq_('foo/bar/bar/foo',Path('foo/bar') + ('bar','foo'))
        eq_('foo/bar/bar/foo',('foo','bar') + Path('bar/foo'))
        eq_('foo/bar/bar/foo','foo/bar' + Path('bar/foo'))
        #Invalid concatenation
        try:
            Path(('foo','bar')) + 1
            self.fail()
        except TypeError:
            pass
    
    def test_path_slice(self):
        foo = Path('foo')
        bar = Path('bar')
        foobar = Path('foo/bar')
        eq_('bar',foobar[foo:])
        eq_('foo',foobar[:bar])
        eq_('foo/bar',foobar[bar:])
        eq_('foo/bar',foobar[:foo])
        eq_((),foobar[foobar:])
        eq_((),foobar[:foobar])
        abcd = Path('a/b/c/d')
        a = Path('a')
        b = Path('b')
        c = Path('c')
        d = Path('d')
        z = Path('z')
        eq_('b/c',abcd[a:d])
        eq_('b/c/d',abcd[a:d+z])
        eq_('b/c',abcd[a:z+d])
        eq_('a/b/c/d',abcd[:z])
    
    def test_add_with_root_path(self):
        """if I perform /a/b/c + /d/e/f, I want /a/b/c/d/e/f, not /a/b/c//d/e/f
        """
        eq_('/foo/bar',str(Path('/foo') + Path('/bar')))
    
    def test_create_with_tuple_that_have_slash_inside(self):
        eq_(('','foo','bar'), Path(('/foo','bar')))
        self.mock(os, 'sep', '\\')
        eq_(('','foo','bar'), Path(('\\foo','bar')))
    
    def test_auto_decode_os_sep(self):
        """Path should decode any either / or os.sep, but always encode in os.sep.
        """
        eq_(('foo\\bar','bleh'),Path('foo\\bar/bleh'))
        self.mock(os, 'sep', '\\')
        eq_(('foo','bar/bleh'),Path('foo\\bar/bleh'))
        path = Path('foo/bar')
        eq_(('foo','bar'),path)
        eq_('foo\\bar',str(path))
    
    def test_contains(self):
        p = Path(('foo','bar'))
        self.assert_(Path(('foo','bar','bleh')) in p)
        self.assert_(Path(('foo','bar')) in p)
        self.assert_('foo' in p)
        self.assert_('bleh' not in p)
        self.assert_(Path('foo') not in p)
    
    def test_windows_drive_letter(self):
        p = Path(('c:',))
        eq_('c:\\',str(p))
    
    def test_root_path(self):
        p = Path('/')
        eq_('/',str(p))
    
    def test_str_encodes_unicode_to_getfilesystemencoding(self):
        p = Path(('foo',u'bar\u00e9'))
        eq_(u'foo/bar\u00e9'.encode(sys.getfilesystemencoding()),str(p))
    
    def test_unicode(self):
        p = Path(('foo',u'bar\u00e9'))
        eq_(u'foo/bar\u00e9',unicode(p))
    
    def test_str_repr_of_mix_between_non_ascii_str_and_unicode(self):
        u = u'foo\u00e9'
        encoded = u.encode(sys.getfilesystemencoding())
        p = Path((encoded,u'bar'))
        eq_('%s/bar' % encoded,str(p))
    
    def test_Path_of_a_Path_returns_self(self):
        #if Path() is called with a path as value, just return value.
        p = Path('foo/bar')
        self.assert_(Path(p) is p)
    
    def test_log_unicode_errors(self):
        # When an there's a UnicodeDecodeError on path creation, log it so it can be possible
        # to debug the cause of it.
        self.mock(sys, 'getfilesystemencoding', lambda: 'ascii')
        assert_raises(UnicodeDecodeError, Path, [u'', 'foo\xe9'])
        assert repr('foo\xe9') in self.logged.getvalue()
    
