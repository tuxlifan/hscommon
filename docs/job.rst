========================================
:mod:`job` - Manage job progress
========================================

.. module:: job

When doing complex processing that has to report progress indication to the user, things can get complex quick. This module helps managing that complexity. It exposes the :class:`Job` class, which track its own progress and reports it through a callback. It can also spawn sub-jobs making tracking progress of multi-steps processes easier.

The ``Job`` class
=================

.. class:: Job(job_proportions, callback)

    A ``Job`` instance represents one or more unit of work. The amount of work each of this units represent is defined in ``job_proportions``. If, for example, you have a job that has 2 units of work with the first one taking roughly twice as much time as the second, you would create your ``Job`` with a ``job_proportions`` at ``[2, 1]``.

    The ``callback`` argument is what lets the user know about the job's progress. It's a callable that takes ``(progress, description='')`` as arguments (it must not require the ``description`` argument). ``progress`` is an integer between 0 and 100. ``description`` is a string describing what is currently being done. When empty, it simply means that the previous description hasn't changed.

    Example usage::

        def big_process(callback_from_gui):
            j = Job([2, 1], callback_from_gui)
            j.start_job(3, 'first step of the big process!')
            # do a first thing
            j.add_progress()
            # do a second thing
            j.add_progress()
            # do a third thing
            j.add_progress()

            # now for the second part
            for i in j.iter_with_progress(xrange(10), 'second part!'):
                # do some processing

    .. method:: add_progress(progress=1, desc='')

        Add ``progress`` units of progress to the current work unit. Send description ``desc`` to the callback.

    .. method:: iter_with_progress(sequence, desc_format=None, every=1)

        Yields each element of ``sequence`` by first calling :meth:``start_job`` on self with progress units equal to the length of ``sequence``. At each yields, :meth:``add_progress`` is called. If ``desc_format`` is not None, a new description is generated from the format at every ``every`` element. For example, such a format could be "Processed %d elements out of %d". If you have a lot of elements in ``sequence``, it might be a good idea to make ``every`` higher so that description formatting doesn't affect your process performance too much.

    .. method:: start_job(max_progress=100, desc='')

        Start a new unit of work on the current job. ``max_progress`` is the units of progress you have in this work unit. Set ``desc`` to set a new description to the callback.

    .. method:: start_subjob(jobcount, desc='')

        Splits the current unit of work between ``jobcount`` jobs. This returns a :class:`Job` instance, which you *must* use until their progress is finished before calling anything else of ``self`` again. If you don't do that, progresses will be all messed up.

        This method is useful when you have a process that has a variable number of work units, and that the number of work units is only known after the process have started. If, for example, you have a 2 phases big process, but that before the second phase, you **might** have some (lengthy) cleanup to do. In this case, if you indeed have a cleanup phase to run before the second phase, you'd call ``start_subjob(2)``, and then call the cleanup phase and finally your second phase with the ``Job`` instance returned by your ``start_subjob`` call.

    .. method:: set_progress(progress, desc='')

        Set the progress of the current work unit to ``progress``, additionally with ``desc`` being sent to the callback.

The ``NullJob`` class
=====================

This class is used when you want to call a function that takes a :class:`Job` as an argument, but that you don't care about job progress. Instead of setting up a dummy job, use ``job.nulljob``, which is a ``NullJob`` instance.

The ``ThreadedJobPerformer`` class
==================================

This class provides an easy way to asynchronously start a job and track its progress. You would use it like this::

    tp = ThreadedJobPerformer()
    j = tp.create_job()
    tp.async_run(some_big_processing, args=(j, ))
    # Now, have the GUI in the main thread constantly check tp.last_progress and
    # tp.last_desc and update a progress dialog or something.
