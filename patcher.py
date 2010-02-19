# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-19
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime
import time
import os

class Patcher(object):
    def __init__(self, target_module=None):
        self._patched = []
        self._patched_osstat = {} # path: os.stat_result
        self._target_module = target_module
    
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
            for key, value in self._target_module.__dict__.iteritems():
                if value is oldvalue:
                    self.patch(self._target_module, key, replace_with)
    
    def patch_osstat(self, path, st_mode=16877, st_ino=742635, st_dev=234881026, st_nlink=51,
        st_uid=501, st_gid=20, st_size=1734, st_atime=1257942648, st_mtime=1257873561, 
        st_ctime=1257873561):
        """ Patches os.stat for `path`.
        
        Patching os.stat can be tricky, because it can mess much more than what you're trying to test.
        Also, it can be cumbersome to do it. This method lets you do it easily. Just specify a path
        for which you want to patch os.stat, and specify the values through **kwargs. The defaults
        here are just some stats (that make sense) to fill up.
        
        Example call: self.patch_osstat(Path('foo/bar'), st_mtime=42)
        """
        if not self._patched_osstat: # first osstat mock, actually install the mock
            old_osstat = os.stat
            def fake_osstat(path_str):
                try:
                    return self._patched_osstat[path_str]
                except KeyError:
                    return old_osstat(path_str)
            self.patch(os, 'stat', fake_osstat)
        st_seq = [st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime]
        self._patched_osstat[unicode(path)] = os.stat_result(st_seq)
    
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
    
