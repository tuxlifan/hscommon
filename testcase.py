# Created By: Virgil Dupras
# Created On: 2007/06/23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import unittest
import datetime
import gc
import logging
import os.path as op
import shutil
import tempfile
import threading
import time
from StringIO import StringIO
import os

from .path import Path

class TestCase(unittest.TestCase):
    cls_tested_module = None
    
    def run(self, result=None):
        self._created_directories = []
        self._mocked = []
        self._mocked_osstat = {} # path: os.stat_result
        self.logged = StringIO(u'')
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        mockhandler = logging.StreamHandler(self.logged)
        mockhandler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
        logger.addHandler(mockhandler)
        self.superSetUp()
        unittest.TestCase.run(self, result)
        self.jointhreads()
        if self._created_directories:
            gc.collect() # Forces instances that hold file resources to be freed allowing tmpdir clearance to work.
        for path in self._created_directories:
            if op.exists(path):
                shutil.rmtree(path)
        # We use reversed() so the original value is put back, even if we mock twice.
        for target, attrname, old_value in reversed(self._mocked):
            setattr(target, attrname, old_value)
    
    def jointhreads(self):
        """Join all threads to the main thread"""
        for thread in threading.enumerate():
            if hasattr(thread, 'BUGGY'):
                continue
            if thread.getName() != 'MainThread' and thread.isAlive():
                if hasattr(thread, 'close'):
                    thread.close()
                thread.join(1)
                if thread.isAlive():
                    print "Thread problem. Some thread doesn't want to stop."
                    thread.BUGGY = True
    
    def mock(self, target, attrname, replace_with):
        ''' Replaces 'target' attribute 'attrname' with 'replace_with' and put it back to normal at
            tearDown.
            
            The very nice thing about mock() is that it will scan self.cls_tested_module for the 
            mock target and mock it as well. This is to fix the "from" imports problem (Where even
            if you mock(os, 'path'), if the tested module imported it with "from os import path",
            the mock will not work).
        '''
        oldvalue = getattr(target, attrname)
        self._mocked.append((target, attrname, oldvalue))
        setattr(target, attrname, replace_with)
        if (self.cls_tested_module is not None) and (self.cls_tested_module is not target):
            for key, value in self.cls_tested_module.__dict__.iteritems():
                if value is oldvalue:
                    self.mock(self.cls_tested_module, key, replace_with)
    
    def mock_osstat(self, path, st_mode=16877, st_ino=742635, st_dev=234881026, st_nlink=51,
        st_uid=501, st_gid=20, st_size=1734, st_atime=1257942648, st_mtime=1257873561, 
        st_ctime=1257873561):
        """ Mocks os.stat for `path`.
        
        Mocking os.stat can be tricky, because it can mess much more than what you're trying to test.
        Also, it can be cumbersome to do it. This method let's you do it easily. Just specify a path
        for which you want to mock os.stat, and specify the values through **kwargs. The defaults
        here are just some stats (that make sense) to fill up.
        
        Example call: self.mock_osstat(Path('foo/bar'), st_mtime=42)
        """
        if not self._mocked_osstat: # first osstat mock, actually install the mock
            old_osstat = os.stat
            def fake_osstat(path_str):
                try:
                    return self._mocked_osstat[path_str]
                except KeyError:
                    return old_osstat(path_str)
            self.mock(os, 'stat', fake_osstat)
        st_seq = [st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime]
        self._mocked_osstat[unicode(path)] = os.stat_result(st_seq)
    
    def mock_today(self, year, month, day):
        '''Mocks today's date to date(year, month, day)
        '''
        # For the mocking to work system wide, time.time() must be mocked. However, there is no way
        # to get a time.time() value out of a datetime, so a timedelta must be used
        new_today = datetime.date(year, month, day)
        today = datetime.date.today()
        time_now = time.time()
        delta = today - new_today
        self.mock(time, 'time', lambda: time_now - (delta.days * 24 * 60 * 60))
    
    @classmethod
    def datadirpath(cls):
        return Path(__file__)[:-1] + ('tests', 'testdata')
    
    @classmethod
    def filepath(cls, relative_path, *args):
        """Returns the path of a file in testdata.
        
        'relative_path' can be anythin that can be added to a Path
        if args is not empty, it will be joined to relative_path
        """
        # I know, the name is not the greatest ever, but it can't start with "test"
        if args:
            relative_path = op.join([relative_path] + list(args))
        current_cls = cls
        while hasattr(current_cls, 'datadirpath'):
            testpath = current_cls.datadirpath()
            result = unicode(testpath + relative_path)
            if op.exists(result):
                break
            current_cls = current_cls.__bases__[0]
        assert op.exists(result)
        return result
    
    def tmpdir(self, ref=None):
        ''' Creates a new temp directory for you to put stuff in.
        
            You don't have to worry about cleaning it up, it's automatically cleaned up on tearDown.
        '''
        result = tempfile.mkdtemp()
        self._created_directories.append(result)
        if ref is not None:
            shutil.rmtree(result)
            shutil.copytree(ref,result)
        return result
    
    def tmppath(self, ref=None):
        return Path(self.tmpdir(ref))
    
    def superSetUp(self):
        """Override this for stuff you want to perform before test runs (even before setUp). It is
        intended for cases where you have a root test case for which you need a common setup code but
        you don't want all your subclasses to require calling the superclass's setUp() every time."""
    
