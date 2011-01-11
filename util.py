# Created By: Virgil Dupras
# Created On: 2011-01-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from . import io

def rem_file_ext(filename):
    """Returns the filename without extension."""
    pos = filename.rfind('.')
    if pos > -1:
        return filename[:pos]
    else:
        return filename

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
    if isinstance(paths, str): # if it's not a string, it's already a list
        paths = paths.split(os.pathsep)
    for path in paths:
        if op.exists(op.join(path, name)):
            return op.join(path, name)
    return None
