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
import time
from io import StringIO

from .path import Path
from .testutil import TestData, jointhreads

class Patcher:
    def __init__(self, target_module=None):
        self._patched = []
        self._patched_osstat = {} # path: os.stat_result
        self._target_module = target_module
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()
        return False
    
    def patch(self, target, attrname, replace_with):
        """ Replaces 'target' attribute 'attrname' with 'replace_with' and put it back to normal at
            tearDown.
            
            The very nice thing about patch() is that it will scan target_module for the patch
            target and patch it as well. This is to fix the "from" imports problem (Where even
            if you patch(os, 'path'), if the tested module imported it with "from os import path",
            the patch will not work).
        """
        oldvalue = getattr(target, attrname)
        self._patched.append((target, attrname, oldvalue))
        setattr(target, attrname, replace_with)
        if (self._target_module is not None) and (self._target_module is not target):
            for key, value in self._target_module.__dict__.items():
                if value is oldvalue:
                    self.patch(self._target_module, key, replace_with)
    
    def patch_today(self, year, month, day):
        """Patches today's date to date(year, month, day)
        """
        # For the patching to work system wide, time.time() must be patched. However, there is no way
        # to get a time.time() value out of a datetime, so a timedelta must be used
        new_today = datetime.date(year, month, day)
        today = datetime.date.today()
        time_now = time.time()
        delta = today - new_today
        self.patch(time, 'time', lambda: time_now - (delta.days * 24 * 60 * 60))
    
    def unpatch(self):
        # We use reversed() so the original value is put back, even if we patch twice.
        for target, attrname, old_value in reversed(self._patched):
            setattr(target, attrname, old_value)
    

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
        jointhreads()
    
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
    
