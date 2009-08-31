# Created By: Virgil Dupras
# Created On: 2006/02/21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import os
import sys
from itertools import takewhile, izip

class Path(tuple):
    """A handy class to work with paths.
    
    path[index] returns a string
    path[start:stop] returns a Path
    start and stop can be int, but the can also be path instances. When start
    or stop are Path like in refpath[p1:p2], it is the same thing as typing
    refpath[len(p1):-len(p2)], except that it will only slice out stuff that are
    equal. For example, 'a/b/c/d'['a/z':'z/d'] returns 'b/c', not ''.
    See the test units for more details.
    
    You can use the + operator, which is the same thing as with tuples, but
    returns a Path.
    
    In HS applications, all paths variable should be Path instances. These Path instances should
    be converted to str only at the last moment (when it is needed in an external function, such
    as os.rename)
    """
    def __new__(cls, value, separator=None):
        def unicode_if_needed(s):
            if isinstance(s, unicode):
                return s
            else:
                try:
                    return unicode(s, sys.getfilesystemencoding())
                except UnicodeDecodeError:
                    logging.warning("Could not decode %r", s)
                    raise
        
        if isinstance(value, Path):
            return value
        if not separator:
            separator = os.sep
        if isinstance(value, basestring):
            if value:
                if (separator not in value) and ('/' in value):
                    separator = '/'
                value = value.split(separator)
            else:
                value = ()
        else:
            #value is a tuple/list
            if any(separator in x for x in value):
                #We have a component with a separator in it. Let's rejoin it, and generate another path.
                return Path(separator.join(value), separator)
            if any(isinstance(x, unicode) for x in value):
                value = [unicode_if_needed(x) for x in value]
        if (len(value) > 1) and (not value[-1]):
            value = value[:-1] #We never want a path to end with a '' (because Path() can be called with a trailing slash ending path)
        return tuple.__new__(cls, value)
    
    def __add__(self, other):
        other = Path(other)
        if other and (not other[0]):
            other = other[1:]
        return Path(tuple.__add__(self, other))
    
    def __contains__(self, item):
        if isinstance(item, Path):
            return item[:len(self)] == self
        else:
            return tuple.__contains__(self, item)
    
    def __eq__(self, other):
        return tuple.__eq__(self, Path(other))
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            if isinstance(key.start, Path):
                equal_elems = list(takewhile(lambda pair: pair[0] == pair[1], izip(self, key.start)))
                key = slice(len(equal_elems), key.stop, key.step)
            if isinstance(key.stop, Path):
                equal_elems = list(takewhile(lambda pair: pair[0] == pair[1], izip(reversed(self), reversed(key.stop))))
                stop = -len(equal_elems) if equal_elems else None
                key = slice(key.start, stop, key.step)
            return Path(tuple.__getitem__(self, key))
        else:
            return tuple.__getitem__(self, key)
    
    def __getslice__(self, i, j): #I have to override it because tuple uses it.
        return Path(tuple.__getslice__(self, i, j))
    
    def __hash__(self):
        return tuple.__hash__(self)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __radd__(self, other):
        return Path(other) + self
    
    def __str__(self):
        return unicode(self).encode(sys.getfilesystemencoding())
    
    def __unicode__(self):
        if len(self) == 1:
            first = self[0]
            if (len(first) == 2) and (first[1] == ':'): #Windows drive letter
                return first + u'\\'
            elif not len(first): #root directory
                return u'/'
        return unicode(os.sep.join(self))
    
