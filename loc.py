import os
import os.path as op
import shutil
import re

import polib

from . import pygettext

LC_MESSAGES = 'LC_MESSAGES'

def _get_langs(folder):
    return [name for name in os.listdir(folder) if op.isdir(op.join(folder, name))]

def _files_with_ext(folder, ext):
    return [op.join(folder, fn) for fn in os.listdir(folder) if fn.endswith(ext)]

def generate_pot(folders, outpath, keywords):
    pyfiles = []
    for folder in folders:
        for root, dirs, filenames in os.walk(folder):
            keep = [fn for fn in filenames if fn.endswith('.py')]
            pyfiles += [op.join(root, fn) for fn in keep]
    pygettext.main(pyfiles, outpath=outpath, keywords=keywords)

def compile_all_po(base_folder):
    langs = _get_langs(base_folder)
    for lang in langs:
        pofolder = op.join(base_folder, lang, LC_MESSAGES)
        pofiles = _files_with_ext(pofolder, '.po')
        for pofile in pofiles:
            p = polib.pofile(pofile)
            p.save_as_mofile(pofile[:-3] + '.mo')

def merge_locale_dir(target, mergeinto):
    langs = _get_langs(target)
    for lang in langs:
        if not op.exists(op.join(mergeinto, lang)):
            continue
        mofolder = op.join(target, lang, LC_MESSAGES)
        mofiles = _files_with_ext(mofolder, '.mo')
        for mofile in mofiles:
            shutil.copy(mofile, op.join(mergeinto, lang, LC_MESSAGES))

def merge_pots_into_pos(folder):
    # We're going to take all pot files in `folder` and for each lang, merge it with the po file
    # with the same name.
    potfiles = _files_with_ext(folder, '.pot')
    for potfile in potfiles:
        refpot = polib.pofile(potfile)
        refname = op.splitext(op.basename(potfile))[0]
        for lang in _get_langs(folder):
            po = polib.pofile(op.join(folder, lang, LC_MESSAGES, refname + '.po'))
            po.merge(refpot)
            po.save()

#--- Cocoa
def all_lproj_paths(folder):
    return _files_with_ext(folder, '.lproj')

def unescape_cocoa_strings(s):
    return s.replace('\\\\', '\\').replace('\\"', '"').replace('\\n', '\n')

def strings2pot(target, dest):
    with open(target, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    # We're reading an en.lproj file. We only care about the righthand part of the translation.
    re_trans = re.compile(r'".*" = "(.*)";')
    strings = re_trans.findall(contents)
    po = polib.pofile(dest)
    addcount = 0
    for s in strings:
        s = unescape_cocoa_strings(s)
        entry = po.find(s)
        if entry is None:
            addcount += 1
            entry = polib.POEntry(msgid=s)
            po.append(entry)
        # we don't know or care about a line number so we put 0
        entry.occurrences.append((target, '0'))
    po.save()

def allstrings2pot(lprojpath, dest, excludes=None):
    allstrings = _files_with_ext(lprojpath, '.strings')
    if excludes:
        allstrings = [p for p in allstrings if op.splitext(op.basename(p))[0] not in excludes]
    for strings_path in allstrings:
        strings2pot(strings_path, dest)
