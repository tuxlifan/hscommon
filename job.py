#!/usr/bin/env python
"""
Unit Name: hs.job.py
Created By: Virgil Dupras
Created On: 2004/12/20
Last modified by:$Author: virgil $
Last modified on:$Date: 2009-05-28 15:19:49 +0200 (Thu, 28 May 2009) $
                 $Revision: 4383 $
Copyright 2004-2005 Hardcoded Software (http://www.hardcoded.net)
Description: unit for the Job.
How to use the job manager:

The Job has been created to simplify that calculation of the progress of
a multi-level task. To use it, first create a "mainjob", which is an instance
of the Job. the initial jobcount parameter is usually 1. However, it can
be more depending of the situation. The callback is usually the "Update" method
of a wx.ProgressDialog.

Your work functions should take a jobmanager instance in parameter. Every
subfunction called by the main work function and with a significant workload
should also receive a job instance in parameter. Every function should
create a subjob instance by calling job.StartSobJob.

Example: Let's say that We have a function ProcessMatrix(matrix,job) and that
our ProcessMatrix function calls ProcessRow(row,job), and that our ProcessRow
calls ProcessCell(row,col,job). ProcessMatrix would receive a mainjob instance
created like this: mainjob = Job(1,progressdialog.Update). Our functions
would look like this:

def ProcessMatrix(matrix,job):
    subjob = job.start_subjob(matrix.GetRowCount())
    for row in matrix:
        ProcessRow(row,subjob)

def ProcessRow(row,job):
    job.start_job(row.GetColCount())
    for col in row:
        ProcessCell(row,col,subjob)
        job.add_progress()

def ProcessCell(row,col)
    DoStuff()
"""
from threading import Thread
import sys

class JobCancelled(Exception):
    "The user has cancelled the job"

class JobInProgressError(Exception): 
    "A job is already being performed, you can't perform more than one at the same time."

class JobCountError(Exception):
    "The number of jobs started have exceeded the number of jobs allowed"

class Job(object):
    """Manages a job's progression and return it's progression through a callback.
    
    Note that this class is not foolproof. For example, you could call
    start_subjob, and then call add_progress from the parent job, and nothing
    would stop you from doing it. However, it would mess your progression
    because it is the sub job that is supposed to drive the progression.
    Another example would be to start a subjob, then start another, and call
    add_progress from the old subjob. Once again, it would mess your progression.
    There are no stops because it would remove the lightweight aspect of the
    class (A Job would need to have a Parent instead of just a callback,
    and the parent could be None. A lot of checks for nothing.).
    Another one is that nothing stops you from calling add_progress right after
    SkipJob.
    """
    #---Magic functions
    def __init__(self, job_proportions, callback):
        """Initialize the Job with 'jobcount' jobs. Start every job with
        start_job(). Every time the job progress is updated, 'callback' is called
        'callback' takes a 'progress' int param, and a optional 'desc'
        parameter. Callback must return false if the job must be cancelled.
        """
        if not hasattr(callback, '__call__'):
            raise TypeError("'callback' MUST be set when creating a Job")
        if isinstance(job_proportions, int):
            job_proportions = [1] * job_proportions
        self._job_proportions = list(job_proportions)
        self._jobcount = sum(job_proportions)
        self._callback = callback
        self._current_job = 0
        self._passed_jobs = 0
        self._progress = 0
        self._currmax = 1
    
    #---Private
    def _subjob_callback(self, progress, desc=''):
        """This is the callback passed to children jobs.
        """
        self.set_progress(progress, desc)
        return True #if JobCancelled has to be raised, it will be at the highest level
    
    def _do_update(self, desc):
        """Calls the callback function with a % progress as a parameter.
        
        The parameter is a int in the 0-100 range.
        """
        passed_progress = self._passed_jobs * self._currmax
        current_progress = self._current_job * self._progress
        total_progress = self._jobcount * self._currmax
        progress = ((passed_progress + current_progress) * 100) // total_progress
        # It's possible that callback doesn't support a desc arg
        result = self._callback(progress, desc) if desc else self._callback(progress)
        if not result:
            raise JobCancelled
    
    #---Public
    def add_progress(self, progress=1, desc=''):
        self.set_progress(self._progress + progress, desc)
    
    def iter_with_progress(self, sequence, desc_format=None, every=1):
        ''' Iterate through sequence while automatically adding progress.
        '''
        desc = ''
        if desc_format:
            desc = desc_format % (0, len(sequence))
        self.start_job(len(sequence), desc)
        for i, element in enumerate(sequence):
            yield element
            count = i + 1
            if desc_format and count % every == 0:
                desc = desc_format % (count, len(sequence))
            self.add_progress(desc=desc)
        if desc_format:
            desc = desc_format % (len(sequence), len(sequence))
        self.set_progress(100, desc)
    
    def start_job(self, max_progress=100, desc=''):
        """Begin work on the next job. You must not call start_job more than
        'jobcount' (in __init__) times.
        'max' is the job units you are to perform.
        'desc' is the description of the job.
        """
        self._passed_jobs += self._current_job
        try:
            self._current_job = self._job_proportions.pop(0)
        except IndexError:
            raise JobCountError
        self._progress = 0
        self._currmax = max(1, max_progress)
        self._do_update(desc)
    
    def start_subjob(self, jobcount, desc=''):
        """Starts a sub job. Use this when you want to split a job into
        multiple smaller jobs. Pretty handy when starting a process where you
        know how many subjobs you will have, but don't know the work unit count
        for every of them.
        returns the Job object
        """
        self.start_job(100, desc)
        return Job(jobcount, self._subjob_callback)
    
    def set_progress(self, progress, desc=''):
        """Sets the progress of the current job to 'progress', and call the
        callback
        """
        self._progress = progress
        if self._progress > self._currmax:
            self._progress = self._currmax
        if self._progress < 0:
            self._progress = 0
        self._do_update(desc)
    

nulljob = Job(0xfffff, lambda p, d='':True)

class ThreadedJobPerformer(object):
    """Run threaded jobs and track progress.
    
    To run a threaded job, first create a job with _create_job(), then call _run_threaded(), with 
    your work function as a parameter.
        
    Example:
        
    j = self._create_job()
    self._run_threaded(self.some_work_func, (arg1, arg2, j))
    """
    _job_running = False
    _last_error = None
    
    #--- Protected
    def create_job(self):
        if self._job_running:
            raise JobInProgressError()
        self.last_progress = -1
        self.last_desc = ''
        self.job_cancelled = False
        return Job(1, self._update_progress)
    
    def _async_run(self, *args):
        target = args[0]
        args = tuple(args[1:])
        self._job_running = True
        self._last_error = None
        try:
            target(*args)
        except JobCancelled:
            pass
        except Exception:
            self._last_error = sys.exc_info()
        finally:
            self._job_running = False
            self.last_progress = None
    
    def _reraise_if_error(self):
        """Reraises the error that happened in the thread if any.
        
        Call this after the caller of run_threaded detected that self._job_running returned to False
        """
        if self._last_error is not None:
            type, value, tb = self._last_error
            raise type, value, tb
    
    def _update_progress(self, newprogress, newdesc=''):
        self.last_progress = newprogress
        if newdesc:
            self.last_desc = newdesc
        return not self.job_cancelled
    
    def run_threaded(self, target, args=()):
        if self._job_running:
            raise JobInProgressError()
        args = (target, ) + args
        Thread(target=self._async_run, args=args).start()
    
