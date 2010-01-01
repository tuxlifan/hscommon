# Created By: Virgil Dupras
# Created On: 2006/02/21
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# About Flags:
# In non-pythonic idioms, we often represent flags in integers, and test the
# flags with binary operations like "if (FLAG & myflags):". This is not very
# pythonic (implicitely, it is not very graceful since python is one of the
# most graceful language ever :).
# Ok. *MY* flags are tuples of integer. Example: (FLAG1,FLAG3,FLAG6), and these
# integer don't need to be "masked" For example, the tuple can be (1,2,3,4,5)
# (Normally, we would need to use (1,2,4,8,16) to avoid overlapping bits).
# Thus, to test for a flag in *MY* system, you can write "if FLAG in flags:"
# The functions below are to convert normal flags to my flag system.
# IMPORTANT NOTE: My flags start at zero. Thus a normal flagset '0x3' = (0,1)
# in my system, not (1,2).

def StrToFlags(s, flagcount=0):
    '''
    StrToFlags('A')   = (0,6)
    StrToFlags('A',4) = (0)
    StrToFlags('AB')  = (1,6,8,14)
    '''
    flagval = 0
    i = 0
    for char in s:
        flagval += ord(char) << ((len(s) - i - 1)*8)
        i += 1
    if flagcount == 0:
        flagcount = len(s)*8
    return IntToFlags(flagval,flagcount)

def IntToFlags(intflags, flagcount=32):
    '''
    IntToFlags(0xf0,8) == (4,5,6,7)
    IntToFlags(0xf0,6) == (4,5)
    '''
    return tuple([i for i in xrange(flagcount) if (intflags >> i) & 1])

def FlagsToInt(flags):
    try:
        result = 0
        for flag in flags:
            result += 1 << flag
        return result
    except TypeError:
        raise TypeError,"A flag must be a tuple of integers. Current: " + str(flags)

def cond(condition, true_value, false_value):
    '''Return true_value if condition is true, and false_value otherwise.
    '''
    if condition:
        return true_value
    else:
        return false_value

def nonone(value, replace_value):
    ''' Returns value if value is not None. Returns replace_value otherwise.
    '''
    if value is None:
        return replace_value
    else:
        return value

def stripnone(seq):
    ''' Returns a sequence with all None elements stripped out of seq.
    '''
    return [x for x in seq if x is not None]

def dedupe(iterable):
    '''Returns a list of elements in iterable with all dupes removed.
    '''
    result = []
    seen = {}
    for item in iterable:
        if item in seen:
            continue
        seen[item] = 1
        result.append(item)
    return result

def flatten(iterables, start_with=None):
    '''Takes a list of lists 'lists' and returns a list containing elements of every list.
    
    If start_with is not None, the result will start with start_with items, exactly as if
    start_with would be the first item of lists.
    '''
    result = []
    if start_with:
        result.extend(start_with)
    for iterable in iterables:
        result.extend(iterable)
    return result

def allsame(iterable):
    """Returns whether all elements of 'iterable' are the same.
    """
    it = iter(iterable)
    try:
        first_item = it.next()
    except StopIteration:
        raise ValueError("iterable cannot be empty")
    return all(element == first_item for element in it)

def first(iterable):
    """Returns the first item of 'iterable'
    """
    try:
        return iter(iterable).next()
    except StopIteration:
        return None

def extract(predicate, iterable):
    """Separates the wheat from the shaft (`predicate` defines what's the wheat), and returns both.
    """
    wheat = []
    shaft = []
    for item in iterable:
        if predicate(item):
            wheat.append(item)
        else:
            shaft.append(item)
    return wheat, shaft

def trydef(func, args, default=None):
    '''
    Applies func with args (args is wrapped in a tuple if it's not already a
    tuple) and return default if an exception is raised. For example,
    trydef(int,'',12) returns 12 and trydef(int,'24',12) returns 24
    '''
    if not isinstance(args, tuple):
        args = (args,)
    try:
        return func(*args)
    except:
        return default

def tryint(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
