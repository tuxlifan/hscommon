========================================
:mod:`misc` - Miscellaneous utilities
========================================

.. module:: misc

.. function:: cond(condition, true_value, false_value)

    Return ``true_value`` if condition is true, and ``false_value`` otherwise.

.. function:: nonone(value, replace_value)
    
    Returns ``value`` if value is not None. Returns ``replace_value`` otherwise.

.. function:: stripnone(seq)
    
    Returns a sequence with all ``None`` elements stripped out of ``seq``.

.. function:: dedupe(iterable)
    
    Returns a list of elements in ``iterable`` with all dupes removed. The order of the elements is preserved.

.. function:: flatten(iterables, start_with=None)
    
    Takes the list of iterable ``iterables`` and returns a list containing elements of every iterable.
    
    If ``start_with`` is not None, the result will start with ``start_with`` items, exactly as if ``start_with`` would be the first item of lists.

.. function:: allsame(iterable)
    
    Returns whether all elements of ``iterable`` are the same. Raises ``ValueError`` if ``iterable`` is empty.

.. function:: first(iterable)
    
    Returns the first item of ``iterable`` or ``None`` if empty.

.. function:: extract(predicate, iterable)
    
    Separates the wheat from the shaft (`predicate` defines what's the wheat), and returns ``(wheat, shaft)``.

.. function:: trydef(func, args, default=None)

    Applies ``func`` with ``args`` and return ``default`` if an exception is raised. For example, ``trydef(int, '', 12)`` returns ``12`` and ``trydef(int, '24', 12)`` returns ``24``.

.. function:: tryint(value, default=0)
    
    Shortcut for ``trydef(int, value, default)``.
