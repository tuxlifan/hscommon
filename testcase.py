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
from io import StringIO
import os

from .path import Path
from .testutil import Patcher, TestData

class TestCase(unittest.TestCase, TestData):
    cls_tested_module = None
    
    def run(self, result=None):
        self.global_setup()
        unittest.TestCase.run(self, result)
        self.global_teardown()
    
    def global_setup(self):
        self._created_directories = []
        self._patcher = Patcher(target_module=self.cls_tested_module)
        self.logged = StringIO('')
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        mockhandler = logging.StreamHandler(self.logged)
        mockhandler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
        logger.addHandler(mockhandler)
        self.superSetUp()
    
    def global_teardown(self):
        self.jointhreads()
        if self._created_directories:
            gc.collect() # Forces instances that hold file resources to be freed allowing tmpdir clearance to work.
        for path in self._created_directories:
            if op.exists(path):
                shutil.rmtree(path)
        self._patcher.unpatch()
    
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
                    print("Thread problem. Some thread doesn't want to stop.")
                    thread.BUGGY = True
    
    def mock(self, *args, **kw):
        self._patcher.patch(*args, **kw)
    
    def mock_osstat(self, *args, **kw):
        self._patcher.patch_osstat(*args, **kw)
    
    def mock_today(self, *args, **kw):
        self._patcher.patch_today(*args, **kw)
    
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
    
