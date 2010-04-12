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

from .str import rem_file_ext

def print_and_do(cmd):
    print cmd
    p = Popen(cmd, shell=True)
    p.wait()

def build_all_qt_ui(base_dir='.'):
    from PyQt4.uic import compileUiDir
    mapper = lambda d, f: (d, rem_file_ext(f) + '_ui.py')
    compileUiDir(base_dir, map=mapper)

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

# This is a method to hack around those freakingly tricky data inclusion/exlusion rules
# in setuptools. We copy the packages *without data* in a build folder and then build the plugin
# from there.
def copy_packages(packages_names, dest):
    ignore = shutil.ignore_patterns('.hg', 'tests', 'testdata', 'modules', 'docs')
    for package_name in packages_names:
        dest_name = op.basename(package_name) # the package name can be a path as well
        dest_path = op.join(dest, dest_name)
        print "Copying package {0} to {1}".format(package_name, dest_path)
        shutil.copytree(package_name, dest_path, ignore=ignore)

def copy_qt_plugins(folder_names, dest): # This is only for Windows
    from .files import find_in_path
    qmake_path = find_in_path('qmake.exe')
    print repr(qmake_path)
    qt_dir = op.split(op.dirname(qmake_path))[0]
    print repr(qt_dir)
    qt_plugin_dir = op.join(qt_dir, 'plugins')
    def ignore(path, names):
        if path == qt_plugin_dir:
            return [n for n in names if n not in folder_names]
        else:
            return [n for n in names if not n.endswith('.dll')]
    shutil.copytree(qt_plugin_dir, dest, ignore=ignore)

def build_debian_changelog(yamlfile, destfile, pkgname, from_version=None):
    """Builds a debian changelog out of a YAML changelog.
    """
    import yaml
    def desc2list(desc):
        # We take each item, enumerated with the '*' character, and transform it into a list.
        desc = desc.replace('\n', ' ')
        desc = desc.replace('  ', ' ')
        result = desc.split('*')
        return [s.strip() for s in result if s.strip()]
    
    ENTRY_MODEL = "{pkg} ({version}) stable; urgency=low\n\n{changes}\n -- Virgil Dupras <hsoft@hardcoded.net>  {date}\n\n"
    CHANGE_MODEL = "  * {description}\n"
    changelogs = yaml.load(open(yamlfile))
    if from_version:
        # We only want logs from a particular version
        for index, log in enumerate(changelogs):
            if log['version'] == from_version:
                changelogs = changelogs[:index+1]
                break
    rendered_logs = []
    for log in changelogs:
        version = log['version']
        logdate = log['date']
        desc = log['description']
        rendered_date = logdate.strftime('%a, %d %b %Y 00:00:00 +0000')
        rendered_descs = [CHANGE_MODEL.format(description=d) for d in desc2list(desc)]
        changes = ''.join(rendered_descs)
        rendered_log = ENTRY_MODEL.format(pkg=pkgname, version=version, changes=changes, date=rendered_date)
        rendered_logs.append(rendered_log)
    result = ''.join(rendered_logs)
    fp = open(destfile, 'w')
    fp.write(result)
    fp.close()
