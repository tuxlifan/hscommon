# Created By: Virgil Dupras
# Created On: 2007-10-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# HS code should only deal with Path instances, not string paths. One of the annoyances of this
# is to always have to convert Path instances with unicode() when calling open() or listdir() etc..
# this unit takes care of this

import __builtin__
import os
import os.path
import shutil
import logging

from .path import Path

def log_io_error(func):
    """ Catches OSError, IOError and WindowsError and log them
    """
    def wrapper(path, *args, **kwargs):
        try:
            return func(path, *args, **kwargs)
        except (IOError, OSError) as e:
            msg = 'Error "{0}" during operation "{1}" on "{2}": "{3}"'
            classname = e.__class__.__name__
            funcname = func.func_name
            logging.warn(msg.format(classname, funcname, unicode(path), unicode(e)))
    
    return wrapper

def path2str(path):
    # Most of the time, we want a simple path --> unicode conversion, but in rare cases, the 
    # filesystem encoding is all messed up. Path instances automatically take care of these, but we
    # still have to wrap the path around str() instead of unicode.
    if not isinstance(path, Path):
        return path
    if path.bogus_encoding:
        return str(path)
    else:
        return unicode(path)

def copy(source_path, dest_path):
    return shutil.copy(path2str(source_path), path2str(dest_path))

def copytree(source_path, dest_path, *args, **kwargs):
    return shutil.copytree(path2str(source_path), path2str(dest_path), *args, **kwargs)

def exists(path):
    return os.path.exists(path2str(path))

def isdir(path):
    return os.path.isdir(path2str(path))

def isfile(path):
    return os.path.isfile(path2str(path))

def islink(path):
    return os.path.islink(path2str(path))

def listdir(path):
    return os.listdir(path2str(path))

def mkdir(path, *args, **kwargs):
    return os.mkdir(path2str(path), *args, **kwargs)

def makedirs(path, *args, **kwargs):
    return os.makedirs(path2str(path), *args, **kwargs)

def move(source_path, dest_path):
    return shutil.move(path2str(source_path), path2str(dest_path))

def open(path, *args, **kwargs):
    return __builtin__.open(path2str(path), *args, **kwargs)

def remove(path):
    return os.remove(path2str(path))

def rename(source_path, dest_path):
    return os.rename(path2str(source_path), path2str(dest_path))

def rmdir(path):
    return os.rmdir(path2str(path))

def rmtree(path):
    return shutil.rmtree(path2str(path))

def stat(path):
    return os.stat(path2str(path))
