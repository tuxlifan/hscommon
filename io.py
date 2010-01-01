# Created By: Virgil Dupras
# Created On: 2007-10-23
# $Id$
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

def copy(source_path, dest_path):
    return shutil.copy(unicode(source_path), unicode(dest_path))

def copytree(source_path, dest_path, *args, **kwargs):
    return shutil.copytree(unicode(source_path), unicode(dest_path), *args, **kwargs)

def exists(path):
    return os.path.exists(unicode(path))

def isdir(path):
    return os.path.isdir(unicode(path))

def isfile(path):
    return os.path.isfile(unicode(path))

def islink(path):
    return os.path.islink(unicode(path))

def listdir(path):
    return os.listdir(unicode(path))

def mkdir(path, *args, **kwargs):
    return os.mkdir(unicode(path), *args, **kwargs)

def makedirs(path, *args, **kwargs):
    return os.makedirs(unicode(path), *args, **kwargs)

def move(source_path, dest_path):
    return shutil.move(unicode(source_path), unicode(dest_path))

def open(path, *args, **kwargs):
    return __builtin__.open(unicode(path), *args, **kwargs)

def remove(path):
    return os.remove(unicode(path))

def rename(source_path, dest_path):
    return os.rename(unicode(source_path), unicode(dest_path))

def rmdir(path):
    return os.rmdir(unicode(path))

def rmtree(path):
    return shutil.rmtree(unicode(path))

def stat(path):
    return os.stat(unicode(path))
