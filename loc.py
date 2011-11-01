import os
import os.path as op
import shutil

from . import pygettext
from . import msgfmt

def _get_langs(folder):
    return [name for name in os.listdir(folder) if op.isdir(op.join(folder, name))]

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
        pofolder = op.join(base_folder, lang, 'LC_MESSAGES')
        pofiles = [op.join(pofolder, fn) for fn in os.listdir(pofolder) if fn.endswith('.po')]
        msgfmt.main(pofiles)

def merge_locale_dir(target, mergeinto):
    langs = _get_langs(target)
    for lang in langs:
        if not op.exists(op.join(mergeinto, lang)):
            continue
        mofolder = op.join(target, lang, 'LC_MESSAGES')
        mofiles = [op.join(mofolder, fn) for fn in os.listdir(mofolder) if fn.endswith('.mo')]
        for mofile in mofiles:
            shutil.copy(mofile, op.join(mergeinto, lang, 'LC_MESSAGES'))