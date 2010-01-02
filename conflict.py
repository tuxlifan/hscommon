# Created By: Virgil Dupras
# Created On: 2008-01-08
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re

#This matches [123], but not [12] (3 digits being the minimum).
#It also matches [1234] [12345] etc..
#And only at the start of the string
re_conflict = re.compile(r'^\[\d{3}\d*\] ')

def get_conflicted_name(other_names, name):
    """Returns name with a [000] number in front of it.
    
    The number between brackets depends on how many conlicted filenames
    there already are in other_names.
    """
    name = get_unconflicted_name(name)
    if name not in other_names:
        return name
    i = 0
    while True:
        newname = '[%03d] %s' % (i, name)
        if newname not in other_names:
            return newname
        i += 1

def get_unconflicted_name(name):
    return re_conflict.sub('',name,1)

def is_conflicted(name):
    return re_conflict.match(name) is not None
