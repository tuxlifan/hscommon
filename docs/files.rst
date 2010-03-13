===========================================
:mod:`files` - Manipulate files and folders
===========================================

.. module:: files

.. function:: open_if_filename(infile, mode='rb')

    If ``infile`` is a string, it opens and returns it. If it's already a file object, it simply returns it. This function returns ``(file, should_close_flag)``. The should_close_flag is True is a file has effectively been opened (if we already pass a file object, we assume that the responsibility for closing the file has already been taken). Example usage::
    
        fp, shouldclose = open_if_filename(infile)
        dostuff()
        if shouldclose:
            fp.close()
    
.. class:: FileOrPath(file_or_path, mode='rb')

    Does the same as :func:`open_if_filename`, but it can be used with a ``with`` statement. Example::
    
        with FileOrPath(infile):
            dostuff()
    
.. function:: clean_empty_dirs(path, deleteself=False, files_to_delete=[])

    Remove all empty folders inside ``path`` recursively. If ``deleteself`` is True and ``path`` ends up being empty, it is deleted as well. ``files_to_delete`` is a list of filenames that we wish to ignore when we determine if a folder is empty or not (for example, those pesky ".DS_Store" files under OS X).

.. function:: delete_if_empty(path, files_to_delete=[])

    Same as with :func:`clean_empty_dirs`, but not recursive.

.. function:: copy(source_path, dest_path)

    Copies ``source_path`` to ``dest_path``, recursively. However, it does conflict resolution using the :mod:`conflict` module.

.. function:: move(source_path, dest_path)

    Same as :func:`copy`, but it moves files instead.

.. function:: modified_after(first_path, second_path)

    Returns True if ``first_path``'s mtime is higher than ``second_path``'s mtime.