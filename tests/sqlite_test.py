# Created By: Virgil Dupras
# Created On: 2007/05/19
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import time
import threading
import os
import os.path as op
import sqlite3 as sqlite

from ..testcase import TestCase
from ..sqlite import ThreadedConn

class TCThreadedConn(TestCase):
    ''' Threading is hard to test. In a lot of those tests, a failure means that the test run will
        hang forever. Well... I don't know a better alternative.
    '''
    def test_can_access_from_multiple_threads(self):
        def run():
            con.execute('insert into foo(bar) values(\'baz\')')
        
        con = ThreadedConn(':memory:', True)
        con.execute('create table foo(bar TEXT)')
        t = threading.Thread(target=run)
        t.start()
        t.join()
        result = con.execute('select * from foo')
        self.assertEqual(1, len(result))
        self.assertEqual('baz', result[0][0])
    
    def test_exception_during_query(self):
        con = ThreadedConn(':memory:', True)
        con.execute('create table foo(bar TEXT)')
        self.assertRaises(sqlite.OperationalError, con.execute, 'select * from bleh')
    
    def test_not_autocommit(self):
        tmpdir = self.tmpdir()
        con = ThreadedConn(op.join(tmpdir, 'foo.db'), False)
        con.execute('create table foo(bar TEXT)')
        con.execute('insert into foo(bar) values(\'baz\')')
        del con
        #The data shouldn't have been inserted
        con = ThreadedConn(op.join(tmpdir, 'foo.db'), False)
        result = con.execute('select * from foo')
        self.assertEqual(0, len(result))
        con.execute('insert into foo(bar) values(\'baz\')')
        con.commit()
        del con
        # Now the data should be there
        con = ThreadedConn(op.join(tmpdir, 'foo.db'), False)
        result = con.execute('select * from foo')
        self.assertEqual(1, len(result))
    
    def test_rollback(self):
        con = ThreadedConn(':memory:', False)
        con.execute('create table foo(bar TEXT)')
        con.execute('insert into foo(bar) values(\'baz\')')
        con.rollback()
        result = con.execute('select * from foo')
        self.assertEqual(0, len(result))
    
    def test_query_palceholders(self):
        con = ThreadedConn(':memory:', True)
        con.execute('create table foo(bar TEXT)')
        con.execute('insert into foo(bar) values(?)', ['baz'])
        result = con.execute('select * from foo')
        self.assertEqual(1, len(result))
        self.assertEqual('baz', result[0][0])
    
    def test_make_sure_theres_no_messup_between_queries(self):
        def run(expected_rowid):
            time.sleep(0.1)
            result = con.execute('select rowid from foo where rowid = ?', [expected_rowid])
            assert expected_rowid == result[0][0]
        
        con = ThreadedConn(':memory:', True)
        con.execute('create table foo(bar TEXT)')
        for i in range(100):
            con.execute('insert into foo(bar) values(\'baz\')')
        threads = []
        for i in range(1, 101):
            t = threading.Thread(target=run, args=(i,))
            t.start
            threads.append(t)
        while threads:
            time.sleep(0.1)
            threads = [t for t in threads if t.isAlive()]
    
    def test_query_after_close(self):
        con = ThreadedConn(':memory:', True)
        con.close()
        con.execute('select 1')
    
    def test_lastrowid(self):
        # It's not possible to return a cursor because of the threading, but lastrowid should be
        # fetchable from the connection itself
        con = ThreadedConn(':memory:', True)
        con.execute('create table foo(bar TEXT)')
        con.execute('insert into foo(bar) values(\'baz\')')
        self.assertEqual(1, con.lastrowid)
    
    def test_add_fetchone_fetchall_interface_to_results(self):
        con = ThreadedConn(':memory:', True)
        con.execute('create table foo(bar TEXT)')
        con.execute('insert into foo(bar) values(\'baz1\')')
        con.execute('insert into foo(bar) values(\'baz2\')')
        result = con.execute('select * from foo')
        ref = result[:]
        self.assertEqual(ref, result.fetchall())
        self.assertEqual(ref[0], result.fetchone())
        self.assertEqual(ref[1], result.fetchone())
        self.assert_(result.fetchone() is None)
    
    def test_non_ascii_dbname(self):
        tmpdir = self.tmpdir()
        ThreadedConn(op.join(tmpdir, u'foo\u00e9.db'), True)
    
    def test_non_ascii_dbdir(self):
        # when this test fails, it doesn't fail gracefully, it brings the whole test suite with it.
        tmpdir = self.tmpdir()
        os.mkdir(op.join(tmpdir, u'foo\u00e9'))
        ThreadedConn(op.join(tmpdir, u'foo\u00e9', 'foo.db'), True)
    
