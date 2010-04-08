# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op

from . import io
from . import conflict

def open_if_filename(infile, mode='rb'):
    """
    infile can be either a string or a file-like object.
    if it is a string, a file will be opened with mode.
    Returns a tuple (shouldbeclosed,infile) infile is a file object
    """
    if isinstance(infile, basestring):
        return (open(infile, mode), True)
    else:
        return (infile, False)

class FileOrPath(object):
    def __init__(self, file_or_path, mode='rb'):
        self.file_or_path = file_or_path
        self.mode = mode
        self.mustclose = False
        self.fp = None
    
    def __enter__(self):
        self.fp, self.mustclose = open_if_filename(self.file_or_path, self.mode)
        return self.fp
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.fp and self.mustclose:
            self.fp.close()
    

def clean_empty_dirs(path, deleteself=False, files_to_delete=[]):
    """Recursively delete empty dirs in directory. 'directory' is deleted only
    if empty and 'deleteself' is True.
    Returns the list of delete paths.
    files_to_delete: The name is clear enough. However, files in
        this list will ONLY be deleted if it makes the directory deletable
        thereafter (In other words, if the directory contains files not in the
        list, NO file will be deleted)
    """
    result = []
    subdirs = [name for name in io.listdir(path) if io.isdir(path + name)]
    for subdir in subdirs:
        result.extend(clean_empty_dirs(path + subdir, True, files_to_delete))
    if deleteself and delete_if_empty(path, files_to_delete):
        result.append(unicode(path))
    return result

@io.log_io_error
def delete_if_empty(path, files_to_delete=[]):
    ''' Deletes the directory at 'path' if it is empty or if it only contains files_to_delete.
    '''
    if not io.exists(path) or not io.isdir(path):
        return
    contents = io.listdir(path)
    if any(name for name in contents if (name not in files_to_delete) or io.isdir(path + name)):
        return False
    for name in contents:
        io.remove(path + name)
    io.rmdir(path)
    return True

def _move_or_copy(operation, source_path, dest_path):
    ''' Use move() or copy() to move and copy file with the conflict management, but without the
        slowness of the fs system.
    '''
    if io.isdir(dest_path):
        dest_path = dest_path + source_path[-1]
    if io.exists(dest_path):
        filename = dest_path[-1]
        dest_dir_path = dest_path[:-1]
        newname = conflict.get_conflicted_name(io.listdir(dest_dir_path), filename)
        dest_path = dest_dir_path + newname
    operation(source_path, dest_path)
    
def move(source_path, dest_path):
    _move_or_copy(io.move, source_path, dest_path)

def copy(source_path, dest_path):
    _move_or_copy(io.copy, source_path, dest_path)

def modified_after(first_path, second_path):
    """Returns True if first_path's mtime is higher than second_path's mtime."""
    try:
        first_mtime = io.stat(first_path).st_mtime
    except EnvironmentError:
        return False
    try:
        second_mtime = io.stat(second_path).st_mtime
    except EnvironmentError:
        return True
    return first_mtime > second_mtime

def find_in_path(name, paths=None):
    """Search for `name` in all directories of `paths` and return the absolute path of the first
    occurrence. If `paths` is None, $PATH is used.
    """
    if paths is None:
        paths = os.environ['PATH']
    if isinstance(paths, basestring): # if it's not a string, it's already a list
        paths = paths.split(os.pathsep)
    for path in paths:
        if op.exists(op.join(path, name)):
            return op.join(path, name)
    return None