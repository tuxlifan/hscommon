# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest
import warnings
from nose.tools import eq_

from ..str import *

class TCStrUtils(unittest.TestCase):
    def test_get_file_ext(self):
        self.assertEqual(get_file_ext("foobar"),"")
        self.assertEqual(get_file_ext("foo.bar"),"bar")
        self.assertEqual(get_file_ext("foobar."),"")
        self.assertEqual(get_file_ext(".foobar"),"foobar")
    
    def test_rem_file_ext(self):
        self.assertEqual(rem_file_ext("foobar"),"foobar")
        self.assertEqual(rem_file_ext("foo.bar"),"foo")
        self.assertEqual(rem_file_ext("foobar."),"foobar")
        self.assertEqual(rem_file_ext(".foobar"),"")

    def test_format_size(self):
        self.assertEqual(format_size(1024),'1 KB')
        self.assertEqual(format_size(1024,2),'1.00 KB')
        self.assertEqual(format_size(1024,0,2),'1 MB')
        self.assertEqual(format_size(1024,2,2),'0.01 MB')
        self.assertEqual(format_size(1024,3,2),'0.001 MB')
        self.assertEqual(format_size(1024,3,2,False),'0.001')
        self.assertEqual(format_size(1023),'1023 B')
        self.assertEqual(format_size(1023,0,1),'1 KB')
        self.assertEqual(format_size(511,0,1),'1 KB')
        self.assertEqual(format_size(9),'9 B')
        self.assertEqual(format_size(99),'99 B')
        self.assertEqual(format_size(999),'999 B')
        self.assertEqual(format_size(9999),'10 KB')
        self.assertEqual(format_size(99999),'98 KB')
        self.assertEqual(format_size(999999),'977 KB')
        self.assertEqual(format_size(9999999),'10 MB')
        self.assertEqual(format_size(99999999),'96 MB')
        self.assertEqual(format_size(999999999),'954 MB')
        self.assertEqual(format_size(9999999999),'10 GB')
        self.assertEqual(format_size(99999999999),'94 GB')
        self.assertEqual(format_size(999999999999),'932 GB')
        self.assertEqual(format_size(9999999999999),'10 TB')
        self.assertEqual(format_size(99999999999999),'91 TB')
        self.assertEqual(format_size(999999999999999),'910 TB')
        self.assertEqual(format_size(9999999999999999),'9 PB')
        self.assertEqual(format_size(99999999999999999),'89 PB')
        self.assertEqual(format_size(999999999999999999),'889 PB')
        self.assertEqual(format_size(9999999999999999999),'9 EB')
        self.assertEqual(format_size(99999999999999999999),'87 EB')
        self.assertEqual(format_size(999999999999999999999),'868 EB')
        self.assertEqual(format_size(9999999999999999999999),'9 ZB')
        self.assertEqual(format_size(99999999999999999999999),'85 ZB')
        self.assertEqual(format_size(999999999999999999999999),'848 ZB')
        
    def test_format_size_negative(self):
        self.assertEqual(format_size(-1024,3,2,False),'-0.001')
        self.assertEqual(format_size(-1024,3,2),'-0.001 MB')
    
    def test_format_size_doesnt_give_warning(self):
        warnings.resetwarnings()
        warnings.filterwarnings('error')
        try:
            format_size(1024)
        except OverflowError:
            self.fail()
        warnings.resetwarnings()
        warnings.filterwarnings('always')
    
    def test_format_time(self):
        self.assertEqual(format_time(0),'00:00:00')
        self.assertEqual(format_time(1),'00:00:01')
        self.assertEqual(format_time(23),'00:00:23')
        self.assertEqual(format_time(60),'00:01:00')
        self.assertEqual(format_time(101),'00:01:41')
        self.assertEqual(format_time(683),'00:11:23')
        self.assertEqual(format_time(3600),'01:00:00')
        self.assertEqual(format_time(3754),'01:02:34')
        self.assertEqual(format_time(36000),'10:00:00')
        self.assertEqual(format_time(366666),'101:51:06')
        self.assertEqual(format_time(0,FT_MINUTES),'00:00')
        self.assertEqual(format_time(1,FT_MINUTES),'00:01')
        self.assertEqual(format_time(23,FT_MINUTES),'00:23')
        self.assertEqual(format_time(60,FT_MINUTES),'01:00')
        self.assertEqual(format_time(101,FT_MINUTES),'01:41')
        self.assertEqual(format_time(683,FT_MINUTES),'11:23')
        self.assertEqual(format_time(3600,FT_MINUTES),'60:00')
        self.assertEqual(format_time(6036,FT_MINUTES),'100:36')
        self.assertEqual(format_time(60360,FT_MINUTES),'1006:00')
        self.assertEqual(format_time(0,FT_DECIMAL),'0.0 second')
        self.assertEqual(format_time(1,FT_DECIMAL),'1.0 second')
        self.assertEqual(format_time(23,FT_DECIMAL),'23.0 seconds')
        self.assertEqual(format_time(60,FT_DECIMAL),'1.0 minute')
        self.assertEqual(format_time(101,FT_DECIMAL),'1.7 minutes')
        self.assertEqual(format_time(683,FT_DECIMAL),'11.4 minutes')
        self.assertEqual(format_time(3600,FT_DECIMAL),'1.0 hour')
        self.assertEqual(format_time(6036,FT_DECIMAL),'1.7 hours')
        self.assertEqual(format_time(86400,FT_DECIMAL),'1.0 day')
        self.assertEqual(format_time(160360,FT_DECIMAL),'1.9 days')
    
    def test_format_time_negative(self):
        self.assertEqual(format_time(-1),'-00:00:01')
        self.assertEqual(format_time(-1,FT_MINUTES),'-00:01')
        self.assertEqual(format_time(-1,FT_DECIMAL),'-1.0 second')
    
    def test_pluralize(self):
        self.assertEqual('0 song',pluralize(0,'song'))
        self.assertEqual('1 song',pluralize(1,'song'))
        self.assertEqual('2 songs',pluralize(2,'song'))
        self.assertEqual('1 song',pluralize(1.1,'song'))
        self.assertEqual('2 songs',pluralize(1.5,'song'))
        self.assertEqual('1.1 songs',pluralize(1.1,'song',1))
        self.assertEqual('1.5 songs',pluralize(1.5,'song',1))
        self.assertEqual('2 entries', pluralize(2,'entry', plural_word='entries'))

    def test_str_replace(self):
        self.assertEqual('136',multi_replace('123456',('2','45')))
        self.assertEqual('1 3 6',multi_replace('123456',('2','45'),' '))
        self.assertEqual('1 3  6',multi_replace('123456','245',' '))
        self.assertEqual('173896',multi_replace('123456','245','789'))
        self.assertEqual('173896',multi_replace('123456','245',('7','8','9')))
        self.assertEqual('17386',multi_replace('123456',('2','45'),'78'))
        self.assertEqual('17386',multi_replace('123456',('2','45'),('7','8')))
        try:
            self.assertEqual('17386',multi_replace('123456',('2','45'),('7','8','9')))
            self.fail()
        except ValueError:
            pass
        self.assertEqual('17346',multi_replace('12346',('2','45'),'78'))
    
    def test_sqlite_escape(self):
        self.assertEqual('foobar',sqlite_escape('foobar'))
        self.assertEqual('foo\'\'bar',sqlite_escape('foo\'bar'))
    
    def test_escape(self):
        self.assertEqual('f\\o\\ob\\ar', escape('foobar', 'oa'))
        self.assertEqual('f*o*ob*ar', escape('foobar', 'oa', '*'))
    
    def test_escape_re(self):
        self.assertEqual('\\(\\)\\[\\]\\\\\\*\\.\\|\\+\\?\\^abc', escape_re('()[]\\*.|+?^abc'))
    

class TCprocess_tokens(unittest.TestCase):
    def test_empty(self):
        self.assertEqual('',process_tokens('',{}))

    def test_no_token(self):
        self.assertEqual('foobar',process_tokens('foobar',{}))

    def test_simple(self):
        self.assertEqual('foo bar',process_tokens('%foo% %bar%',{'foo':lambda : 'foo','bar':lambda : 'bar'}))

    def test_unsupported_tokens(self):
        self.assertEqual('foo (none)',process_tokens('%foo% %bar%',{'foo':lambda : 'foo'}))

    def test_tokens_with_params(self):
        def foo(p1,p2):
            return 'foo %s %s' % (p1,p2)
        def bar(p1 = 'default'):
            return 'bar %s' % p1
        self.assertEqual('(none) bar default',process_tokens('%foo% %bar%',{'foo': foo,'bar': bar}))
        self.assertEqual('foo 1 2 bar 1',process_tokens('%foo:1:2% %bar:1%',{'foo': foo,'bar': bar}))
        self.assertEqual('(none) (none)',process_tokens('%foo:1:2:3% %bar:1:2%',{'foo': foo,'bar': bar}))

    def test_tokens_with_data(self):
        """If the data parameter passed to ProcessToken is not None,
        the handlers will have this data parameter as their first parameter.
        """
        def foobar(data):
            return data
        data = 'foo'
        self.assertEqual('foo',process_tokens('%foobar%',{'foobar':foobar},data))
        data = 'bar'
        self.assertEqual('bar',process_tokens('%foobar%',{'foobar':foobar},data))

    def test_single_handler(self):
        def handler(token):
            return token
        def handler_with_data(token,data):
            return "%s-%s" % (token,data)
        self.assertEqual('foobar',process_tokens('%foobar%',handler))
        self.assertEqual('foo-bar',process_tokens('%foo%',handler_with_data,'bar'))

    def test_param_with_whitespaces(self):
        def handler(token,param):
            self.assertEqual('foobar',token)
            self.assertEqual('foo bar',param)
            return param
        self.assertEqual('foo bar',process_tokens('%foobar:foo bar%',handler))
    

def test_remove_invalid_xml():
    eq_(remove_invalid_xml(u'foo\0bar\x0bbaz'), u'foo bar baz')
    # surrogate blocks have to be replaced, but not the rest
    eq_(remove_invalid_xml(u'foo\ud800bar\udfffbaz\ue000'), u'foo bar baz\ue000')
    # replace with something else
    eq_(remove_invalid_xml('foo\0baz', replace_with='bar'), 'foobarbaz')

warnings.resetwarnings()
warnings.filterwarnings('always') #So that the warning test for format_size works.
