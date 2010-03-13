========================================
:mod:`io` - Wrapper for io functions
========================================

.. module:: io

When using :class:`path.Path` instances, it can become cumbersome to constantly wrap your paths around ``unicode()`` calls whenever you use an IO call. For this reason, this module wraps IO calls used throughout HS apps and convert paths to strings there.

.. function:: copy(source_path, dest_path)
.. function:: copytree(source_path, dest_path, *args, **kwargs)
.. function:: exists(path)
.. function:: isdir(path)
.. function:: isfile(path)
.. function:: islink(path)
.. function:: listdir(path)
.. function:: mkdir(path, *args, **kwargs)
.. function:: makedirs(path, *args, **kwargs)
.. function:: move(source_path, dest_path)
.. function:: open(path, *args, **kwargs)
.. function:: remove(path)
.. function:: rename(source_path, dest_path)
.. function:: rmdir(path)
.. function:: rmtree(path)
.. function:: stat(path)
