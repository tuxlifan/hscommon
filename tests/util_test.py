# Created By: Virgil Dupras
# Created On: 2011-01-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..testutil import eq_, patch_osstat
from ..util import rem_file_ext, modified_after

def test_rem_file_ext():
    eq_(rem_file_ext("foobar"), "foobar")
    eq_(rem_file_ext("foo.bar"), "foo")
    eq_(rem_file_ext("foobar."), "foobar")
    eq_(rem_file_ext(".foobar"), "")

class TestCase_modified_after:
    def test_first_is_modified_after(self, monkeypatch):
        patch_osstat(monkeypatch, 'first', st_mtime=42)
        patch_osstat(monkeypatch, 'second', st_mtime=41)
        assert modified_after('first', 'second')
    
    def test_second_is_modified_after(self, monkeypatch):
        patch_osstat(monkeypatch, 'first', st_mtime=42)
        patch_osstat(monkeypatch, 'second', st_mtime=43)
        assert not modified_after('first', 'second')
    
    def test_same_mtime(self, monkeypatch):
        patch_osstat(monkeypatch, 'first', st_mtime=42)
        patch_osstat(monkeypatch, 'second', st_mtime=42)
        assert not modified_after('first', 'second')
    
    def test_first_file_does_not_exist(self, monkeypatch):
        # when the first file doesn't exist, we return False
        patch_osstat(monkeypatch, 'second', st_mtime=42)
        assert not modified_after('does_not_exist', 'second') # no crash
    
    def test_second_file_does_not_exist(self, monkeypatch):
        # when the second file doesn't exist, we return True
        patch_osstat(monkeypatch, 'first', st_mtime=42)
        assert modified_after('first', 'does_not_exist') # no crash
    
