# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import os
import sys
from itertools import takewhile, izip

# Sometimes, filesystems have filenames in the wrong encoding. That's tricky. In these cases, what
# we do is to decode them in latin-1 (which is the most common non-utf8 encoding). This encoding
# will decode all characters, so even if this decoding might end up with messy characters, at least
# there will be no crash. Moreover, the Path remembers which parts of itself was bogus and re-uses
# FALLBACK_ENCODING when encoding itself. This way, we end up referring to the same file path.
FALLBACK_ENCODING = 'latin-1'

def join(values):
    uni = not values or isinstance(values[0], unicode)
    if len(values) == 1:
        first = values[0]
        if (len(first) == 2) and (first[1] == ':'): #Windows drive letter
            return (first + u'\\') if uni else (first + '\\')
        elif not len(first): #root directory
            return u'/' if uni else '/'
    sep = unicode(os.sep) if uni else str(os.sep)
    return sep.join(values)

class Path(object):
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
    def __new__(cls, value, *args, **kwargs):
        if isinstance(value, Path):
            return value
        else:
            return object.__new__(cls)
    
    def __init__(self, value, separator=None, latin1_indexes=None):
        if not latin1_indexes:
            latin1_indexes = set()
        else:
            latin1_indexes = set(latin1_indexes)
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
                self._path = Path(separator.join(value), separator)._path
                self._latin1_indexes = frozenset()
                return
            anyuni = any(isinstance(x, unicode) for x in value)
            alluni = all(isinstance(x, unicode) for x in value)
            if anyuni and not alluni:
                univalues = []
                for i, x in enumerate(value):
                    if isinstance(x, unicode):
                        univalues.append(x)
                    else:
                        try:
                            univalues.append(unicode(x, sys.getfilesystemencoding()))
                        except UnicodeDecodeError:
                            logging.warning("Could not decode %r", x)
                            univalues.append(unicode(x, FALLBACK_ENCODING))
                            latin1_indexes.add(i)
                value = univalues
        if (len(value) > 1) and (not value[-1]):
            value = value[:-1] #We never want a path to end with a '' (because Path() can be called with a trailing slash ending path)
        self._path = tuple(value)
        self._latin1_indexes = frozenset(latin1_indexes)
    
    def __repr__(self):
        return repr(self._path)
    
    def __len__(self):
        return len(self._path)
    
    def __add__(self, other):
        other = Path(other)
        if other and (not other[0]):
            other = other[1:]
        latin1_indexes = self._latin1_indexes
        for i in other._latin1_indexes:
            latin1_indexes.add(i+len(self._path))
        return Path(self._path + other._path, latin1_indexes=latin1_indexes)
    
    def __contains__(self, item):
        if isinstance(item, Path):
            return item[:len(self)] == self
        else:
            return item in self._path
    
    def __eq__(self, other):
        return self._path == Path(other)._path
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            if isinstance(key.start, Path):
                equal_elems = list(takewhile(lambda pair: pair[0] == pair[1], izip(self._path, key.start._path)))
                key = slice(len(equal_elems), key.stop, key.step)
            if isinstance(key.stop, Path):
                equal_elems = list(takewhile(lambda pair: pair[0] == pair[1], izip(reversed(self._path), reversed(key.stop._path))))
                stop = -len(equal_elems) if equal_elems else None
                key = slice(key.start, stop, key.step)
            latin1_indexes = set()
            start = key.start or 0
            stop = key.stop or len(self)
            for i in self._latin1_indexes:
                if start <= i < stop:
                    latin1_indexes.add(i-key.start)
            return Path(self._path.__getitem__(key), latin1_indexes=latin1_indexes)
        else:
            return self._path.__getitem__(key)
    
    def __hash__(self):
        return hash(self._path)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __radd__(self, other):
        return Path(other) + self
    
    def __str__(self):
        if not self._latin1_indexes:
            return unicode(self).encode(sys.getfilesystemencoding())
        else:
            sysenc = sys.getfilesystemencoding()
            values = []
            for i, x in enumerate(self._path):
                if not isinstance(x, unicode):
                    values.append(x)
                elif i in self._latin1_indexes:
                    values.append(x.encode(FALLBACK_ENCODING))
                else:
                    values.append(x.encode(sysenc))
            return join(values)
    
    def __unicode__(self):
        return unicode(join(self._path))
    
    @property
    def bogus_encoding(self):
        return bool(self._latin1_indexes)
    
