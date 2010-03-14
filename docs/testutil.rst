========================================
:mod:`testutil` - Unit testing utilities
========================================

.. module:: testutil

The ``Patcher`` class
=====================

.. class:: Patcher(target_module=None)

    With the ``Patcher``, you can replace objects' attributes with :meth:`patch` and then restore those attributes with :meth:`unpatch`. A nice feature of the ``Patcher`` is that you can specify the modules your testing through ``target_module``. When you do this, the ``Patcher`` will, every time it patches somthing, look into that module for instances of the patched attribute and replace it as well. This is very useful if your tested module use a ``from foo import bar`` import scheme (without target module patching, patching ``foo.bar`` would not patch the instance of ``bar`` which has already been place in your tested module's globals when you first imported it).

    You can also use the ``Patcher`` in a ``with`` context like this::

        with Patcher() as p:
            p.patch(foo, 'bar', 'patched!')
            # assert some stuff
            # no need to call p.unpatch(), it's automatically called on __exit__()

    .. method:: patch(target, attrname, replace_with)

        Replaces ``target``'s attribute ``attrname`` with ``replace_with``.

    .. method:: patch_osstat(path, st_mode=16877, st_ino=742635, st_dev=234881026, st_nlink=51, st_uid=501, st_gid=20, st_size=1734, st_atime=1257942648, st_mtime=1257873561, st_ctime=1257873561)

        Patches the ``os.stat`` function for :class:`path.Path` instance ``path`` with stats specified in the arguments. The defaults arguments are all number that make sense so you can very well just change a few attributes and leave the rest untouched and the numbers will still make sense. The patch only affect ``path``, other paths passed to ``os.stat`` will go through normally.

    .. method:: patch_today(year, month, day)

        Patches ``time.time()`` so that the system thinks that today's date corresponds to the ``year``, ``month`` and ``day`` arguments.

    .. method:: unpatch()

        Undo any patching that this instance made. If this instance is used in a context manager (``with`` statement), you don't need to call this.

The ``TestData`` class
======================

.. class:: TestData

    This is a static class that makes usage of test data easier. When including test files with test units, it's often a pain to have access to it. You need to take ``__file__``, remove the filename element, and then combine it with subpaths. Do it in a few tests, and you'll grow bored and create a class like this. To use it in your test suite, subclass it in a core unit of your test suite, and then override ``datadirpath`` like that::
    
        from hsutil.testutil import TestData as TestDataBase
        from hsutil.path import Path
        
        class TestData(TestDataBase):
            @classmethod
            def datadirpath(cls):
                return Path(__file__)[:-1] + 'testdata_folder'
        
    Then, you can use it easily in your tests::
    
        from .base import TestData
        
        def test_something():
            filepath = TestData.filepath('foo.test')
    
    .. classmethod:: datadirpath()
    
        Returns a :class:`path.Path` pointing to the folder where your test data is. You must override this when subclassing ``TestData``.
    
    .. classmethod:: filepath(relative_path, *args)
    
        Returns a :class:`path.Path` pointing to the file in ``relative_path``, which is relative to ``datadirpath``. If the path doesn't exist, we try to find them in superclasses' ``datadirpath``.
        
        An alternative way to call ``filepath`` is to put each elements of the path in ``*args`` like this::
        
            TestData.filepath('foo', 'bar', 'baz.file')
        
Functions
=========

.. function:: with_tmpdir(func)

    A decorator that creates a temporary directory before calling ``func`` and cleans it afterwards. The path (as a :class:`path.Path` instance) is appended to ``*args``.

.. function:: patch_today(year, month, day)

    Calls ``func`` with today patched (through :meth:`Patcher.patch_today`).
