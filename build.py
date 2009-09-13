# Created By: Virgil Dupras
# Created On: 2009-03-03
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import os.path as op
import shutil
import tempfile

from .str import rem_file_ext

def print_and_do(cmd):
    print cmd
    os.system(cmd)

def build_all_qt_ui(base_dir='.'):
    names = os.listdir(base_dir)
    uinames = [name for name in names if name.endswith('.ui')]
    for name in uinames:
        path = op.join(base_dir, name)
        destpath = rem_file_ext(path) + '_ui.py'
        print_and_do("pyuic4 {0} > {1}".format(path, destpath))

# this is all a big hack to go around the fact that py2app will include stuff in the testdata
# folders and I haven't figured out what options prevent that.

def move_testdata_out(base_dir='.'):
    # looks into backages in 'base_dir', move them into a temp directory and return a list of path
    # to those locations (so it can be put back)
    result = []
    dirnames = [n for n in os.listdir(base_dir) if op.isdir(n) and not n.startswith('.')]
    for dirname in dirnames:
        for nametomove in ['testdata', 'modules']:
            testdatapath = op.join(base_dir, dirname, nametomove)
            if op.exists(testdatapath):
                tmppath = op.join(tempfile.mkdtemp(), nametomove)
                print 'Moving %s to %s' % (testdatapath, tmppath)
                shutil.move(testdatapath, tmppath)
                result.append((testdatapath, tmppath))
    return result

def put_testdata_back(move_log):
    for originalpath, tmppath in move_log:
        print 'Moving %s to %s' % (tmppath, originalpath)
        shutil.move(tmppath, originalpath)