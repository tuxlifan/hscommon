# Created By: Virgil Dupras
# Created On: 2009-03-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from __future__ import unicode_literals

import os
import sys
import os.path as op
import shutil
import tempfile
import plistlib
from subprocess import Popen

from .files import modified_after
from .str import rem_file_ext

def print_and_do(cmd):
    print cmd
    p = Popen(cmd, shell=True)
    os.waitpid(p.pid, 0)

def build_all_qt_ui(base_dir='.'):
    names = os.listdir(base_dir)
    uinames = [name for name in names if name.endswith('.ui')]
    for name in uinames:
        path = op.join(base_dir, name)
        destpath = rem_file_ext(path) + '_ui.py'
        if modified_after(path, destpath):
            print_and_do("pyuic4 {0} > {1}".format(path, destpath))
        else:
            print "{0} is already compiled".format(unicode(path))

def build_dmg(app_path, dest_path):
    print repr(op.join(app_path, 'Contents', 'Info.plist'))
    plist = plistlib.readPlist(op.join(app_path, 'Contents', 'Info.plist'))
    workpath = tempfile.mkdtemp()
    dmgpath = op.join(workpath, plist['CFBundleName'])
    os.mkdir(dmgpath)
    print_and_do('cp -R "%s" "%s"' % (app_path, dmgpath))
    print_and_do('ln -s /Applications "%s"' % op.join(dmgpath, 'Applications'))
    dmgname = '%s_osx_%s.dmg' % (plist['CFBundleName'].lower().replace(' ', '_'), plist['CFBundleVersion'].replace('.', '_'))
    print 'Building %s' % dmgname
    print_and_do('hdiutil create "%s" -format UDZO -nocrossdev -srcdir "%s"' % (op.join(dest_path, dmgname), dmgpath))
    print 'Build Complete'

def add_to_pythonpath(path):
    """Adds `path` to both PYTHONPATH env and sys.path.
    """
    abspath = op.abspath(path)
    pythonpath = os.environ.get('PYTHONPATH', '')
    pathsep = ';' if sys.platform == 'win32' else ':'
    pythonpath = pathsep.join([abspath, pythonpath]) if pythonpath else abspath
    os.environ['PYTHONPATH'] = pythonpath
    sys.path.insert(1, abspath)

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

# This is another method to hack around those freakingly tricky data inclusion/exlusion rules
# in setuptools. Instead of moving data out, we copy the packages *without data* in a build
# folder and then build the plugin from there.

def copy_packages(packages_names, dest):
    ignore = shutil.ignore_patterns('.hg', 'tests', 'testdata', 'modules')
    for packages_name in packages_names:
        dest_path = op.join(dest, packages_name)
        print "Copying package {0} to {1}".format(packages_name, dest_path)
        shutil.copytree(packages_name, dest_path, ignore=ignore)
