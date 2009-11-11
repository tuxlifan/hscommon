# Created By: Virgil Dupras
# Created On: 2006/02/21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from StringIO import StringIO

from .. import io
from ..testcase import TestCase
from ..files import *
from ..path import Path

class TCopen_if_filename(TestCase):
    def test_file_name(self):
        file, close = open_if_filename(self.filepath('utils/test.txt'))
        self.assertTrue(close)
        self.assertEqual('test_data', file.read())
        file.close()
    
    def test_opened_file(self):
        sio = StringIO()
        sio.write('test_data')
        sio.seek(0)
        file, close = open_if_filename(sio)
        self.assertFalse(close)
        self.assertEqual('test_data', file.read())
    
    def test_mode_is_passed_to_open(self):
        file, close = open_if_filename(self.filepath('utils/test.txt'),'a')
        self.assertEqual('a', file.mode)
        file.close()
    

class TCFileOrPath(TestCase):
    def test_path(self):
        with FileOrPath(self.filepath('utils/test.txt')) as fp:
            self.assertEqual('test_data', fp.read())
    
    def test_opened_file(self):
        sio = StringIO()
        sio.write('test_data')
        sio.seek(0)
        with FileOrPath(sio) as fp:
            self.assertEqual('test_data', fp.read())
    
    def test_mode_is_passed_to_open(self):
        with FileOrPath(self.filepath('utils/test.txt'), 'a') as fp:
            self.assertEqual('a', fp.mode)
    

class TCclean_empty_dirs(TestCase):
    def test_clean_empty_dirs(self):
        testdir = Path(self.tmpdir())
        io.mkdir(testdir + 'dir1')
        io.mkdir(testdir + 'dir2')
        io.mkdir(testdir + 'dir3')
        io.mkdir(testdir + 'dir4')
        io.mkdir(testdir + 'dir5')
        io.mkdir(testdir + ('dir1', 'sub1'))
        io.mkdir(testdir + ('dir1', 'sub2'))
        io.mkdir(testdir + ('dir3', 'sub1'))
        fp = io.open(testdir + ('dir1', 'sub2', 'file.test'), 'w')
        fp.write('bleh')
        fp.close()
        fp = io.open(testdir + ('dir5', 'file.test'),'w')
        fp.write('bleh')
        fp.close()
        result = clean_empty_dirs(testdir)
        self.assertEqual(result,
            [
                testdir+('dir1','sub1'),
                testdir+('dir2',),
                testdir+('dir3','sub1'),
                testdir+('dir3',),
                testdir+('dir4',),
            ])
        self.assertEqual(io.listdir(testdir) ,['dir1','dir5'])
        self.assertEqual(io.listdir(testdir + 'dir1') ,['sub2'])
        self.assertEqual(io.listdir(testdir + ('dir1', 'sub2')) ,['file.test'])
        self.assertEqual(io.listdir(testdir + 'dir5') ,['file.test'])
        io.remove(testdir + ('dir1', 'sub2', 'file.test'))
        io.remove(testdir + ('dir5', 'file.test'))
        result = clean_empty_dirs(testdir)
        self.assertEqual(result,
            [
                testdir+('dir1','sub2'),
                testdir+('dir1',),
                testdir+('dir5',),
            ])
        self.assertEqual(io.listdir(testdir), [])
    
    def test_clean_empty_dirs_with_files_to_delete(self):
        testpath = Path(self.tmpdir())
        io.mkdir(testpath + 'dir')
        io.mkdir(testpath + 'dir2')
        io.open(testpath + ('dir', 'file1.test'), 'w')
        io.open(testpath + ('dir', 'file2.test'), 'w')
        result = clean_empty_dirs(testpath, files_to_delete=['file1.test'])
        self.assertEqual(result, [(testpath + 'dir2')])
        result = clean_empty_dirs(testpath, files_to_delete=['file1.test', 'file2.test'])
        self.assertEqual(result, [(testpath + 'dir')])
    

class TCdelete_if_empty(TestCase):
    def test_is_empty(self):
        testpath = Path(self.tmpdir())
        self.assert_(delete_if_empty(testpath))
        self.assert_(not io.exists(testpath))
    
    def test_not_empty(self):
        testpath = Path(self.tmpdir())
        io.mkdir(testpath + 'foo')
        self.assert_(not delete_if_empty(testpath))
        self.assert_(io.exists(testpath))
    
    def test_with_files_to_delete(self):
        testpath = Path(self.tmpdir())
        io.open(testpath + 'foo', 'w')
        io.open(testpath + 'bar', 'w')
        self.assert_(delete_if_empty(testpath, ['foo', 'bar']))
        self.assert_(not io.exists(testpath))
    
    def test_directory_in_files_to_delete(self):
        testpath = Path(self.tmpdir())
        io.mkdir(testpath + 'foo')
        self.assert_(not delete_if_empty(testpath, ['foo']))
        self.assert_(io.exists(testpath))
    
    def test_delete_files_to_delete_only_if_dir_is_empty(self):
        testpath = Path(self.tmpdir())
        io.open(testpath + 'foo', 'w')
        io.open(testpath + 'bar', 'w')
        self.assert_(not delete_if_empty(testpath, ['foo']))
        self.assert_(io.exists(testpath))
        self.assert_(io.exists(testpath + 'foo'))
    
    def test_doesnt_exist(self):
        """When the 'path' doesn't exist, just do nothing"""
        delete_if_empty(Path('does_not_exist')) # no crash
    
    def test_is_file(self):
        """When 'path' is a file, do nothing"""
        p = self.tmppath() + 'filename'
        io.open(p, 'w').close()
        delete_if_empty(p) # no crash
    
    def test_ioerror(self):
        # if an IO error happens during the operation, ignore it.
        def do_raise(*args, **kw):
            raise OSError()
        
        self.mock(io, 'rmdir', do_raise)
        delete_if_empty(self.tmppath()) # no crash
    

class TCmove_copy(TestCase):
    def setUp(self):
        self.path = Path(self.tmpdir())
        io.open(self.path + 'foo', 'w').close()
        io.open(self.path + 'bar', 'w').close()
        io.mkdir(self.path + 'dir')
    
    def test_move_no_conflict(self):
        move(self.path + 'foo', self.path + 'baz')
        self.assert_(io.exists(self.path + 'baz'))
        self.assert_(not io.exists(self.path + 'foo'))
    
    def test_copy_no_conflict(self): # No need to duplicate the rest of the tests... Let's just test on move
        copy(self.path + 'foo', self.path + 'baz')
        self.assert_(io.exists(self.path + 'baz'))
        self.assert_(io.exists(self.path + 'foo'))
    
    def test_move_no_conflict_dest_is_dir(self):
        move(self.path + 'foo', self.path + 'dir')
        self.assert_(io.exists(self.path + ('dir', 'foo')))
        self.assert_(not io.exists(self.path + 'foo'))
    
    def test_move_conflict(self):
        move(self.path + 'foo', self.path + 'bar')
        self.assert_(io.exists(self.path + '[000] bar'))
        self.assert_(not io.exists(self.path + 'foo'))
    
    def test_move_conflict_dest_is_dir(self):
        move(self.path + 'foo', self.path + 'dir')
        move(self.path + 'bar', self.path + 'foo')
        move(self.path + 'foo', self.path + 'dir')
        self.assert_(io.exists(self.path + ('dir', 'foo')))
        self.assert_(io.exists(self.path + ('dir', '[000] foo')))
        self.assert_(not io.exists(self.path + 'foo'))
        self.assert_(not io.exists(self.path + 'bar'))
    

class TCmodified_after(TestCase):
    def test_first_is_modified_after(self):
        self.mock_osstat('first', st_mtime=42)
        self.mock_osstat('second', st_mtime=41)
        assert modified_after('first', 'second')
    
    def test_second_is_modified_after(self):
        self.mock_osstat('first', st_mtime=42)
        self.mock_osstat('second', st_mtime=43)
        assert not modified_after('first', 'second')
    
    def test_same_mtime(self):
        self.mock_osstat('first', st_mtime=42)
        self.mock_osstat('second', st_mtime=42)
        assert not modified_after('first', 'second')
    