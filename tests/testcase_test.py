# Created By: Virgil Dupras
# Created On: 2007/06/23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import shutil
import threading
import time
import logging

from .. import testcase

class TCTestCase(testcase.TestCase):
    def setUp(self):
        self.tmpdir() #this shouldnt fail
    
    def test_tmpdir_created(self):
        path = self.tmpdir()
        self.assert_(op.exists(path))
        self.assertEqual([], os.listdir(path))
    
    def test_tmpdir_is_cleaned_at_tearDown(self):
        class MyTC(testcase.TestCase):
            def test_foo(self):
                self.path = self.tmpdir()
                fd = open(op.join(self.path, 'foo'), 'w')
                fd.write('foo')
                fd.close()
            
        tc = MyTC('test_foo')
        tc.run()
        self.assert_(not op.exists(tc.path))
    
    def test_tmpdir_doesnt_choke_at_tearDown_if_dir_is_already_deleted(self):
        path = self.tmpdir()
        shutil.rmtree(path)
        self.tearDown()
    
    someattr = 'somevalue'
    def test_mock_sets_attribute(self):
        # mock() calls Patcher.patch()
        self.mock(self, 'someattr', 'othervalue')
        self.assertEqual('othervalue', self.someattr)
    
    def test_join_threads(self):
        #In this test, we create 2 threads, one that will be alive and one that will not.
        class MyTC(testcase.TestCase):
            def test_foo(self):
                def process_that_takes_some_time():
                    time.sleep(0.1)
                    self.counter += 1
        
                self.counter = 0
                t = threading.Thread(target=process_that_takes_some_time)
                t.start()
                t.join()
                threading.Thread(target=process_that_takes_some_time).start()
        
        tc = MyTC('test_foo')
        tc.run()
        # tc.run() should have joined the second thread, so the counter should be 2
        self.assertEqual(2, tc.counter)
    
    def test_call_close_on_thread_if_exists(self):
        # If the thread has a close attribute, call it
        class MyTC(testcase.TestCase):
            def test_foo(self):
                class MyThread(threading.Thread):
                    tc = self
                    def close(self):
                        self.tc.called_close = True
                    
                    def run(self):
                        time.sleep(0.1)
                    
                
                self.called_close = False
                MyThread().start()
        
        tc = MyTC('test_foo')
        tc.run()
        # tc.run() should have joined the second thread, so the counter should be 2
        self.assertTrue(tc.called_close)
    
    def test_tmppath(self):
        """TestCase.tmppath() should return the equivalent of Path(TestCase.tmpdir())"""
        self.mock(self, 'tmpdir', lambda ref: 'foo/bar/' + ref)
        self.assertEqual(self.tmppath('baz'), ('foo', 'bar', 'baz'))
    
    def test_logging(self):
        # TestCase captures logging and put it in self.logged
        logging.warning(u'foobar\xe9')
        self.logged.seek(0)
        self.assertEqual(self.logged.read(), u'WARNING:foobar\xe9\n')
    
