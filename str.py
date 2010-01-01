# Created By: Virgil Dupras
# Created On: 2006/02/21
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from math import ceil

from .misc import cond

def escape(s, to_escape, escape_with='\\'):
    return ''.join(cond(c in to_escape, escape_with + c, c) for c in s)

def escape_re(s):
    return escape(s, '()[]\\*.|+?^')

SIZE_DESC = ('B','KB','MB','GB','TB','PB','EB','ZB','YB')
SIZE_VALS = tuple([1024L ** i for i in range(1,9)])
def format_size(size, decimal=0, forcepower=-1, showdesc=True):
    """Transform a byte count in a formatted string (KB, MB etc..).
    
    size is the number of bytes to format.
    decimal is the number digits after the dot.
    forcepower is the desired suffix. 0 is B, 1 is KB, 2 is MB etc.. if kept at -1, the suffix will
    be automatically chosen (so the resulting number is always below 1024).
    if showdesc is True, the suffix will be shown after the number.
    """
    if forcepower < 0:
        i = 0
        while size >= SIZE_VALS[i]:
            i += 1
    else:
        i = forcepower
    if i > 0:
        div = SIZE_VALS[i-1]
    else:
        div = 1
    format = '%%%d.%df' % (decimal,decimal)
    negative = size < 0
    divided_size = ((0.0 + abs(size)) / div)
    if decimal == 0:
        divided_size = ceil(divided_size)
    else:
        divided_size = ceil(divided_size * (10 ** decimal)) / (10 ** decimal)
    if negative:
        divided_size *= -1
    result = format % divided_size
    if showdesc:
        result += ' ' + SIZE_DESC[i]
    return result

FT_MINUTES, FT_HOURS, FT_DECIMAL = range(3)
def format_time(seconds, format=FT_HOURS):
    """Transforms seconds in a hh:mm:ss string.
    
    Possible values for format:
    FT_MINUTES: mm:ss
    FT_HOURS: hh:mm:ss
    FT_DECIMAL: 0.0 *variable suffix* Ex: 2.3 hours
    """
    minus = seconds < 0
    if minus:
        seconds *= -1
    m, s = divmod(seconds, 60)
    if format == FT_MINUTES:
        r = '%02d:%02d' % (m,s)
    elif format == FT_HOURS:
        h, m = divmod(m, 60)
        r = '%02d:%02d:%02d' % (h, m, s)
    else:
        if seconds < 60:
            r = pluralize(seconds, 'second', 1)
        elif seconds < 3600:
            r = pluralize(seconds / 60.0, 'minute', 1)
        elif seconds < 86400:
            r = pluralize(seconds / 3600.0, 'hour', 1)
        else:
            r = pluralize(seconds / 86400.0, 'day', 1)
    if minus:
        return '-' + r
    else:
        return r

def get_file_ext(filename):
    """Returns the lowercase extension part of filename, without the dot."""
    pos = filename.rfind('.')
    if pos > -1:
        return filename[pos + 1:].lower()
    else:
        return ''

def pluralize(number, word, decimals=0, plural_word=None):
    """Returns a string with number in front of s, and adds a 's' to s if number > 1
    
    number: The number to go in front of s
    word: The word to go after number
    decimals: The number of digits after the dot
    plural_word: If the plural rule for word is more complex than adding a 's', specify a plural
    """
    number = round(number, decimals)
    format = "%%1.%df %%s" % decimals
    if number > 1:
        if plural_word is None:
            word += 's'
        else:
            word = plural_word
    return format % (number, word)

def rem_file_ext(filename):
    """Returns the filename without extension."""
    pos = filename.rfind('.')
    if pos > -1:
        return filename[:pos]
    else:
        return filename

def sqlite_escape(s):
    return escape(s, "'", "'")

FS_FORBIDDEN = '/\\:*?"<>|'
def multi_replace(s, replace_from, replace_to=''):
    """A function like str.replace() with multiple replacements.

    replace_from is a list of things you want to replace. Ex: ['a','bc','d']
    replace_to is a list of what you want to replace to.
    If replace_to is a list and has the same length as replace_from, replace_from
    items will be translated to corresponding replace_to. A replace_to list must
    have the same length as replace_from
    If replace_to is a basestring, all replace_from occurence will be replaced
    by that string.
    replace_from can also be a str. If it is, every char in it will be translated
    as if replace_from would be a list of chars. If replace_to is a str and has
    the same length as replace_from, it will be transformed into a list.
    """
    if isinstance(replace_to, basestring) and (len(replace_from) != len(replace_to)):
        replace_to = [replace_to for r in replace_from]
    if len(replace_from) != len(replace_to):
        raise ValueError('len(replace_from) must be equal to len(replace_to)')
    replace = zip(replace_from, replace_to)
    for r_from, r_to in [r for r in replace if r[0] in s]:
        s = s.replace(r_from, r_to)
    return s

re_process_tokens = re.compile('\%[\w:\s]*\%',re.IGNORECASE)

def process_tokens(s, handlers, data=None):
    """Process a token filled (%token%) string using handlers.
    
    s is a string containing tokens. Tokens are words between two
    percent (%) signs. They can optionally contain parameters, which are
    defined with :, like %token:param:other_param%.
    
    handlers is a dictionnary of strings mapped to callable. the string
    represent a supported token name, and the callable must return a string
    that will replace the token. If the callabale returns None, or doesn't
    have the number of parameters matching with the number of params
    present in the token, the token will be substitued by '(none)'
    
    if handlers is a callable instead of a dictionnary, it means that
    the user wants only a single handler. in this case, the token name will be
    passed as the first parameter. if there is a data, data will be the second
    param, and then will follow the sub params.
    
    if data is not None, every handler will receive it as their first
    parameter. Don't forget to think about it when writing your handlers!
    """
    def replace(match):
        result = None
        expression = match.string[match.start()+1:match.end()-1].lower()
        token = expression.split(':')[0]
        params = expression.split(':')[1:]
        if data is not None:
            params.insert(0,data)
        if hasattr(handlers, '__call__'):
            params.insert(0,token)
            handler = handlers
        else:
            handler = handlers.get(token,None)
        if hasattr(handler, '__call__'):
            try:
                result = handler(*params)
            except TypeError:
                pass
        if result is None:
            result = ''
        result = result.replace('\n', ' ').replace('\0', ' ').strip()
        if result == '':
            result = '(none)'
        return result
    
    return re_process_tokens.sub(replace, s)
