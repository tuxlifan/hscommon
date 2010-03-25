========================================
:mod:`str` - String utilities
========================================

.. module:: str

.. function:: escape(s, to_escape, escape_with='\\')
    
    Returns ``s`` with characters in ``to_escape`` all prepended with ``escape_with``.

.. function:: escape_re(s)

    Returns ``s`` with regex special characters escaped.

.. function:: format_size(size, decimal=0, forcepower=-1, showdesc=True)
    
    Transform a byte count ``size`` in a formatted string (KB, MB etc..). ``decimal`` is the number digits after the dot. ``forcepower`` is the desired suffix. 0 is B, 1 is KB, 2 is MB etc.. if kept at -1, the suffix will be automatically chosen (so the resulting number is always below 1024). If ``showdesc`` is True, the suffix will be shown after the number. Usage example::
    
        >>> format_size(1234, decimal=2, showdesc=True)
        '1.21 KB'

.. function:: format_time(seconds, format=FT_HOURS)
    
    Transforms ``seconds`` in a formatted string. Possible values for format:
    
    * FT_MINUTES: mm:ss
    * FT_HOURS: hh:mm:ss
    * FT_DECIMAL: 0.0 *variable suffix* Ex: 2.3 hours
    
    Usage example::
    
        >>> str.format_time(530, str.FT_DECIMAL)
        '8.8 minutes'
        >>> str.format_time(530, str.FT_MINUTES)
        '08:50'

.. function:: get_file_ext(filename)
    
    Returns the lowercase extension part of ``filename``, without the dot.

.. function:: pluralize(number, word, decimals=0, plural_word=None)
    
    Returns a string with ``number`` in front of ``word``, and adds a 's' to ``word`` if ``number`` > 1. If ``plural_word`` is defined, it will replace ``word`` in plural cases instead of appending a 's'.

.. function:: rem_file_ext(filename)
    
    Returns ``filename`` without extension.

.. function:: sqlite_escape(s)
    
    Returns ``s`` with ``'`` characters sqlite-escaped (by doubling them).

.. function:: multi_replace(s, replace_from, replace_to='')
    
    A function like str.replace() with multiple replacements. ``replace_from`` is a list of things you want to replace (Ex: ``['a','bc','d']``). ``replace_to`` is a list of what you want to replace to. If ``replace_to`` is a list and has the same length as ``replace_from``, ``replace_from`` items will be translated to corresponding ``replace_to``. A ``replace_to`` list must have the same length as ``replace_from``. If ``replace_to`` is a string, all ``replace_from`` occurences will be replaced by that string. ``replace_from`` can also be a string. If it is, every char in it will be translated as if ``replace_from`` would be a list of chars. If ``replace_to`` is a string and has the same length as ``replace_from``, it will be transformed into a list.

.. function:: process_tokens(s, handlers, data=None)
    
    Process a token filled (%token%) string using ``handlers``.
    
    ``s`` is a string containing tokens. Tokens are words between two
    percent (%) signs. They can optionally contain parameters, which are
    defined with ``:``, like %token:param:other_param%.
    
    ``handlers`` is a dictionnary of strings mapped to callable. the string
    represent a supported token name, and the callable must return a string
    that will replace the token. If the callabale returns ``None``, or doesn't
    have the number of parameters matching with the number of params
    present in the token, the token will be substitued by '(none)'
    
    If ``handlers`` is a callable instead of a dictionnary, it means that
    the user wants only a single handler. in this case, the token name will be
    passed as the first parameter. if there is a data, data will be the second
    param, and then will follow the sub params.
    
    If ``data`` is not None, every handler will receive it as their first
    parameter. Don't forget to think about it when writing your handlers!
