# Created By: Virgil Dupras
# Created On: 2006/02/21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

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

def minmax(value, min_value, max_value):
    """Returns `value` or one of the min/max bounds if `value` is not between them.
    """
    return min(max(value, min_value), max_value)
