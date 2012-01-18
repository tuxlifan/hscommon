# Created By: Virgil Dupras
# Created On: 2009-03-03
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os
import sys
import os.path as op
import shutil
import tempfile
import plistlib
from subprocess import Popen, PIPE
import re
import importlib
from datetime import datetime
import glob
import sysconfig

from .plat import ISWINDOWS
from .util import rem_file_ext, modified_after, find_in_path

def print_and_do(cmd):
    print(cmd)
    p = Popen(cmd, shell=True)
    p.wait()

def _perform(src, dst, action, actionname):
    if not op.lexists(src):
        return
    if op.lexists(dst):
        os.remove(dst)
    print('%s %s --> %s' % (actionname, src, dst))
    action(src, dst)

def move(src, dst):
    _perform(src, dst, os.rename, 'Moving')

def copy(src, dst):
    _perform(src, dst, shutil.copy, 'Copying')

def symlink(src, dst):
    _perform(src, dst, os.symlink, 'Symlinking')

def _perform_on_all(pattern, dst, action):
    # pattern is a glob pattern, example "folder/foo*". The file is moved directly in dst, no folder
    # structure from src is kept.
    filenames = glob.glob(pattern)
    for fn in filenames:
        destpath = op.join(dst, op.basename(fn))
        action(fn, destpath)

def move_all(pattern, dst):
    _perform_on_all(pattern, dst, move)

def copy_all(pattern, dst):
    _perform_on_all(pattern, dst, copy)

def ensure_empty_folder(path):
    """Make sure that the path exists and that it's an empty folder.
    """
    if op.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

def filereplace(filename, outfilename=None, **kwargs):
    """Reads `filename`, replaces all {variables} in kwargs, and writes the result to `outfilename`.
    """
    if outfilename is None:
        outfilename = filename
    fp = open(filename, 'rt', encoding='utf-8')
    contents = fp.read()
    fp.close()
    # We can't use str.format() because in some files, there might be {} characters that mess with it.
    for key, item in kwargs.items():
        contents = contents.replace('{{{}}}'.format(key), item) 
    fp = open(outfilename, 'wt', encoding='utf-8')
    fp.write(contents)
    fp.close()

def get_module_version(modulename):
    mod = importlib.import_module(modulename)
    return mod.__version__

def get_xcode_version():
    p = Popen(['xcodebuild', '-version'], stdout=PIPE)
    s = p.communicate()[0].decode('latin-1')
    assert s.startswith('Xcode ')
    startpos = len('Xcode ')
    return s[startpos:startpos+3]

def build_all_qt_ui(base_dir='.', from_imports=False):
    from PyQt4.uic import compileUiDir
    mapper = lambda d, f: (d, rem_file_ext(f) + '_ui.py')
    compileUiDir(base_dir, map=mapper, from_imports=from_imports)

def build_all_qt_locs(basedir, extradirs=None):
    """Builds all .ts files in `basedir` and create a .qm file with the same name.
    
    If extradirs is not None, for each .ts file in basedir a .ts file with the same name is sought
    for in extradirs and added to the resulting .qm file.
    """
    if extradirs is None:
        extradirs = []
    tsfiles = [fn for fn in os.listdir(basedir) if fn.endswith('.ts')]
    for ts in tsfiles:
        files_in_cmd = [op.join(basedir, ts)]
        for extradir in extradirs:
            extrats = op.join(extradir, ts)
            if op.exists(extrats):
                files_in_cmd.append(extrats)
        tsfiles_cmd = ' '.join(files_in_cmd)
        destfile = op.join(basedir, ts.replace('.ts', '.qm'))
        print_and_do('lrelease {} -qm {}'.format(tsfiles_cmd, destfile))

def build_dmg(app_path, dest_path):
    print(repr(op.join(app_path, 'Contents', 'Info.plist')))
    plist = plistlib.readPlist(op.join(app_path, 'Contents', 'Info.plist'))
    workpath = tempfile.mkdtemp()
    dmgpath = op.join(workpath, plist['CFBundleName'])
    os.mkdir(dmgpath)
    print_and_do('cp -R "%s" "%s"' % (app_path, dmgpath))
    print_and_do('ln -s /Applications "%s"' % op.join(dmgpath, 'Applications'))
    dmgname = '%s_osx_%s.dmg' % (plist['CFBundleName'].lower().replace(' ', '_'), plist['CFBundleVersion'].replace('.', '_'))
    print('Building %s' % dmgname)
    # UDBZ = bzip compression. UDZO (zip compression) was used before, but it compresses much less.
    print_and_do('hdiutil create "%s" -format UDBZ -nocrossdev -srcdir "%s"' % (op.join(dest_path, dmgname), dmgpath))
    print('Build Complete')

def build_cocoa_localization(model_path, loc_path):
    """Use 'ibtool --strings-file' on all xib in loc_path using 'model_path' as a model.
    
    For example, if you give 'en.lproj' as model_path and 'fr.lproj' as loc_path, this function
    looks in en.lproj for all xibs. For each of them, it looks if there's a .strings file of the
    same name in fr.lproj. If there is, we use ibtool to merge the fr strings file with the en xib
    and write it to fr.lproj. If there's no strings file, the xib is copied over to loc_path
    """
    xibs = [name for name in os.listdir(model_path) if name.endswith('.xib')]
    for xib in xibs:
        basename = rem_file_ext(xib)
        model_xib = op.join(model_path, xib)
        loc_strings = op.join(loc_path, basename+'.strings')
        dest_xib = op.join(loc_path, xib)
        if op.exists(loc_strings):
            if modified_after(model_xib, dest_xib) or modified_after(loc_strings, dest_xib):
                cmd = 'ibtool --strings-file {0} --write {1} {2}'
                print_and_do(cmd.format(loc_strings, dest_xib, model_xib))
        else:
            if modified_after(model_xib, dest_xib):
                print("Copying {0}".format(model_xib))
                shutil.copy(model_xib, dest_xib)

def build_all_cocoa_locs(basedir):
    locs = [name for name in os.listdir(basedir) if name.endswith('.lproj')]
    locs.remove('en.lproj')
    model_path = op.join(basedir, 'en.lproj')
    for loc in locs:
        loc_path = op.join(basedir, loc)
        print("Building {0} localizations".format(loc_path))
        build_cocoa_localization(model_path, loc_path)

def copy_sysconfig_files_for_embed(destpath):
    # This normally shouldn't be needed for Python 3.3+.
    makefile = sysconfig.get_makefile_filename()
    configh = sysconfig.get_config_h_filename()
    shutil.copy(makefile, destpath)
    shutil.copy(configh, destpath)
    with open(op.join(destpath, 'site.py'), 'w') as fp:
        fp.write("""
import os.path as op
from distutils import sysconfig
sysconfig.get_makefile_filename = lambda: op.join(op.dirname(__file__), 'Makefile')
sysconfig.get_config_h_filename = lambda: op.join(op.dirname(__file__), 'pyconfig.h')
""")

def add_to_pythonpath(path):
    """Adds `path` to both PYTHONPATH env and sys.path.
    """
    abspath = op.abspath(path)
    pythonpath = os.environ.get('PYTHONPATH', '')
    pathsep = ';' if ISWINDOWS else ':'
    pythonpath = pathsep.join([abspath, pythonpath]) if pythonpath else abspath
    os.environ['PYTHONPATH'] = pythonpath
    sys.path.insert(1, abspath)

# This is a method to hack around those freakingly tricky data inclusion/exlusion rules
# in setuptools. We copy the packages *without data* in a build folder and then build the plugin
# from there.
def copy_packages(packages_names, dest, create_links=False):
    if ISWINDOWS:
        create_links = False
    ignore = shutil.ignore_patterns('.hg*', 'tests', 'testdata', 'modules', 'docs', 'locale')
    for package_name in packages_names:
        if op.exists(package_name):
            source_path = package_name
        else:
            mod = __import__(package_name)
            source_path = op.dirname(mod.__file__)
        dest_name = op.basename(package_name) # the package name can be a path as well
        dest_path = op.join(dest, dest_name)
        if op.exists(dest_path):
            if op.islink(dest_path):
                os.unlink(dest_path)
            else:
                shutil.rmtree(dest_path)
        print("Copying package at {0} to {1}".format(source_path, dest_path))
        if create_links:
            os.symlink(op.abspath(source_path), dest_path)
        else:
            shutil.copytree(source_path, dest_path, ignore=ignore)

def copy_qt_plugins(folder_names, dest): # This is only for Windows
    qmake_path = find_in_path('qmake.exe')
    qt_dir = op.split(op.dirname(qmake_path))[0]
    qt_plugin_dir = op.join(qt_dir, 'plugins')
    def ignore(path, names):
        if path == qt_plugin_dir:
            return [n for n in names if n not in folder_names]
        else:
            return [n for n in names if not n.endswith('.dll')]
    shutil.copytree(qt_plugin_dir, dest, ignore=ignore)

def build_debian_changelog(changelogpath, destfile, pkgname, from_version=None):
    """Builds a debian changelog out of a YAML changelog.
    """
    def desc2list(desc):
        # We take each item, enumerated with the '*' character, and transform it into a list.
        desc = desc.replace('\n', ' ')
        desc = desc.replace('  ', ' ')
        result = desc.split('*')
        return [s.strip() for s in result if s.strip()]
    
    ENTRY_MODEL = "{pkg} ({version}) stable; urgency=low\n\n{changes}\n -- Virgil Dupras <hsoft@hardcoded.net>  {date}\n\n"
    CHANGE_MODEL = "  * {description}\n"
    changelogs = read_changelog_file(changelogpath)
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

re_changelog_header = re.compile(r'=== ([\d.]*) \(([\d\-]*)\)')
def read_changelog_file(filename):
    def iter_by_three(it):
        while True:
            version = next(it)
            date = next(it)
            description = next(it)
            yield version, date, description
    
    with open(filename, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    splitted = re_changelog_header.split(contents)[1:] # the first item is empty
    # splitted = [version1, date1, desc1, version2, date2, ...]
    result = []
    for version, date_str, description in iter_by_three(iter(splitted)):
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        d = {'date': date, 'date_str': date_str, 'version': version, 'description': description.strip()}
        result.append(d)
    return result
