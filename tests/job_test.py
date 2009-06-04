# Unit Name: hsutil.tests.job_test
# Created By: Virgil Dupras
# Created On: 2005/04/07
# $Id$
# Copyright 2007 Hardcoded Software (http://www.hardcoded.net)

import unittest

from .. import job

class TCJob(unittest.TestCase):
    def setUp(self):
        self.cancel = False
        self.lastprogress = 0
        self.lastdesc = ''
    
    def callback(self,progress,desc=''):
        #progress is the % of total progression.
        self.lastprogress = progress
        self.lastdesc = desc
        return not self.cancel
    
    def testBase(self):
        j = job.Job(3,self.callback)
        j.start_job(10,'foobar')
        self.assertEqual(self.lastprogress,0)
        self.assertEqual(self.lastdesc,'foobar')
        j.add_progress()
        self.assertEqual(self.lastprogress,3) # (1 / (10 * 3)) * 100
        self.assertEqual(self.lastdesc,'')
        j.add_progress()
        self.assertEqual(self.lastprogress,6) # (2 / (10 * 3)) * 100
        j.add_progress(3)
        self.assertEqual(self.lastprogress,16) # (5 / (10 * 3)) * 100
        j.add_progress(5)
        self.assertEqual(self.lastprogress,33) # (10 / (10 * 3)) * 100
        j.add_progress(5) #The job only supports 10 units
        self.assertEqual(self.lastprogress,33) # (10 / (10 * 3)) * 100
        j.set_progress(7) # Go back to 7
        self.assertEqual(self.lastprogress,23) # (7 / (10 * 3)) * 100
        j.add_progress(3)
        self.assertEqual(self.lastprogress,33) # (10 / (10 * 3)) * 100
        j.start_job()
        j.set_progress(100)
        self.assertEqual(self.lastprogress,66)
        self.assertEqual(self.lastdesc,'')
        j.start_job(50,'barfoo')
        self.assertEqual(self.lastprogress,66)
        self.assertEqual(self.lastdesc,'barfoo')
        j.add_progress(-50) # This shouldn't work
        self.assertEqual(self.lastprogress,66)
        j.add_progress(5)
        self.assertEqual(self.lastprogress,70) # (105 / (50 * 3)) * 100
        j.add_progress(100)
        self.assertEqual(self.lastprogress,100)
        try:
            j.start_job()
            self.fail()
        except job.JobCountError:
            pass
    
    def testSubJobs(self):
        j1 = job.Job(2,self.callback)
        j2 = j1.start_subjob(3,'foobar')
        self.assertEqual(self.lastprogress,0)
        self.assertEqual(self.lastdesc,'foobar')
        j2.add_progress(6) #No job is started in j2 yet. Nothing is done
        self.assertEqual(self.lastprogress,0)
        self.assertEqual(self.lastdesc,'')
        j2.start_job(10,'bleh')
        self.assertEqual(self.lastprogress,0)
        self.assertEqual(self.lastdesc,'bleh') #SubJob description are brought up to the top.
        j2.add_progress()
        self.assertEqual(self.lastprogress,1) # (1 / (10 * 3 * 2)) * 100
        j2.add_progress(3)
        self.assertEqual(self.lastprogress,6) # (4 / (10 * 3 * 2)) * 100
        j2.start_job()
        j2.set_progress(100)
        self.assertEqual(self.lastprogress,33) # (1 / 6) * 100
        #Nothing stops you from calling add_progress/Update after start_job
        #You shouldn't do it, but you can.
        j2.set_progress(15)
        self.assertEqual(self.lastprogress,19) # (115 / (100 * 3 * 2)) * 100
        j2.start_job(25)
        self.assertEqual(self.lastprogress,33) # (50 / (25 * 3 * 2)) * 100
        j2.add_progress(15)
        self.assertEqual(self.lastprogress,43) # (65 / (25 * 3 * 2)) * 100
        j2.add_progress(115)
        self.assertEqual(self.lastprogress,50) # (75 / (25 * 3 * 2)) * 100
        j1.set_progress(42)
        #Nothing stops you from calling add_progress/Update from the parent
        #job when that job called start_subjob. You shouldn't do it, but you can.
        self.assertEqual(self.lastprogress,21) # (42 / (100 * 2)) * 100
        j2 = j1.start_subjob(2,'barfoo')
        self.assertEqual(self.lastprogress,50)
        self.assertEqual(self.lastdesc,'barfoo')
        j2.start_job()
        j2.set_progress(100)
        self.assertEqual(self.lastprogress,75)
        j3 = j2.start_subjob(5)
        self.assertEqual(self.lastprogress,75)
        j3.start_job()
        j3.set_progress(100)
        self.assertEqual(self.lastprogress,80)
        j3.start_job()
        j3.set_progress(100)
        self.assertEqual(self.lastprogress,85)
        j3.start_job()
        j3.set_progress(100)
        self.assertEqual(self.lastprogress,90)
        j3.start_job()
        j3.set_progress(100)
        self.assertEqual(self.lastprogress,95)
        j3.start_job(5)
        self.assertEqual(self.lastprogress,95)
        j3.add_progress()
        self.assertEqual(self.lastprogress,96)
        j3.add_progress(3)
        self.assertEqual(self.lastprogress,99)
        j3.add_progress(37589)
        self.assertEqual(self.lastprogress,100)
        j3.set_progress(2)
        self.assertEqual(self.lastprogress,97)
    
    def test_still_gets_to_100_even_with_rounding_woes(self):
        j = job.Job(1,self.callback)
        j = j.start_subjob(3)
        j.start_job()
        j.start_job()
        j.set_progress(100)
        j = j.start_subjob(1)
        j.start_job(3)
        j.add_progress(3)
        self.assertEqual(100,self.lastprogress)
    
    def test_with_different_job_proportions(self):
        j = job.Job((1,3),self.callback)
        j.start_job(10)
        j.add_progress(5)
        self.assertEqual(int(0.5 * 0.25 * 100),self.lastprogress)
        j.start_job(10)
        j.add_progress(5)
        self.assertEqual(int(25 + (0.5 * 0.75 * 100)),self.lastprogress)
    
    def test_zero_job_max(self):
        #shouldn't raise a zero div error
        j = job.Job(1,self.callback)
        j.start_job(0)
        j.add_progress()
    
    def test_zero_jobcount(self):
        j = job.Job(0,self.callback)
        self.assertRaises(job.JobCountError,j.start_job)
    
    def test_iter_with_progress(self):
        j = job.Job(1, self.callback)
        seq = range(5)
        for i in j.iter_with_progress(seq):
            self.assertEqual(self.lastprogress, i * 20)
        self.assertEqual(self.lastprogress, 100)
    
    def test_iter_with_progress_desc(self):
        # It's possible to pass a desc format to iter_with_progress
        j = job.Job(1, self.callback)
        seq = range(5)
        for i in j.iter_with_progress(seq, 'Processed %d items of %d'):
            self.assertEqual(self.lastdesc, 'Processed %d items of 5' % i)
        self.assertEqual(self.lastdesc, 'Processed 5 items of 5')
    
    def test_iter_with_progress_desc_every(self):
        # It's possible to pass a 'every' arg to iter_with_progress, which is less taxing
        j = job.Job(1, self.callback)
        seq = range(5)
        for i in j.iter_with_progress(seq, 'Processed %d items of %d', 2):
            if i % 2 == 0:
                self.assertEqual(self.lastdesc, 'Processed %d items of 5' % i)
            else:
                self.assertEqual(self.lastdesc, 'Processed %d items of 5' % (i - 1))
        self.assertEqual(self.lastdesc, 'Processed 5 items of 5')
    
