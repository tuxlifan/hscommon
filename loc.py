import os
import os.path as op
import shutil
import re

import polib

from . import pygettext
from .util import modified_after, dedupe

LC_MESSAGES = 'LC_MESSAGES'

def get_langs(folder):
    return [name for name in os.listdir(folder) if op.isdir(op.join(folder, name))]

def files_with_ext(folder, ext):
    return [op.join(folder, fn) for fn in os.listdir(folder) if fn.endswith(ext)]

def generate_pot(folders, outpath, keywords):
    pyfiles = []
    for folder in folders:
        for root, dirs, filenames in os.walk(folder):
            keep = [fn for fn in filenames if fn.endswith('.py')]
            pyfiles += [op.join(root, fn) for fn in keep]
    pygettext.main(pyfiles, outpath=outpath, keywords=keywords)

def compile_all_po(base_folder):
    langs = get_langs(base_folder)
    for lang in langs:
        pofolder = op.join(base_folder, lang, LC_MESSAGES)
        pofiles = files_with_ext(pofolder, '.po')
        for pofile in pofiles:
            p = polib.pofile(pofile)
            p.save_as_mofile(pofile[:-3] + '.mo')

def merge_locale_dir(target, mergeinto):
    langs = get_langs(target)
    for lang in langs:
        if not op.exists(op.join(mergeinto, lang)):
            continue
        mofolder = op.join(target, lang, LC_MESSAGES)
        mofiles = files_with_ext(mofolder, '.mo')
        for mofile in mofiles:
            shutil.copy(mofile, op.join(mergeinto, lang, LC_MESSAGES))

def merge_pots_into_pos(folder):
    # We're going to take all pot files in `folder` and for each lang, merge it with the po file
    # with the same name.
    potfiles = files_with_ext(folder, '.pot')
    for potfile in potfiles:
        refpot = polib.pofile(potfile)
        refname = op.splitext(op.basename(potfile))[0]
        for lang in get_langs(folder):
            po = polib.pofile(op.join(folder, lang, LC_MESSAGES, refname + '.po'))
            po.merge(refpot)
            po.save()

#--- Cocoa
def all_lproj_paths(folder):
    return files_with_ext(folder, '.lproj')

def all_xib_strings(lprojpath):
    xibnames = [op.splitext(op.basename(fn))[0] for fn in os.listdir(lprojpath) if fn.endswith('.xib')]
    stringspaths = [op.join(lprojpath, fn + '.strings') for fn in xibnames]
    return [path for path in stringspaths if op.exists(path)]

def escape_cocoa_strings(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def unescape_cocoa_strings(s):
    return s.replace('\\\\', '\\').replace('\\"', '"').replace('\\n', '\n')

def strings2pot(target, dest):
    with open(target, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    # We're reading an en.lproj file. We only care about the righthand part of the translation.
    re_trans = re.compile(r'".*" = "(.*)";')
    strings = re_trans.findall(contents)
    po = polib.pofile(dest)
    for s in dedupe(strings):
        s = unescape_cocoa_strings(s)
        entry = po.find(s)
        if entry is None:
            entry = polib.POEntry(msgid=s)
            po.append(entry)
        # we don't know or care about a line number so we put 0
        entry.occurrences.append((target, '0'))
    po.save()

def allstrings2pot(lprojpath, dest, excludes=None):
    allstrings = files_with_ext(lprojpath, '.strings')
    if excludes:
        allstrings = [p for p in allstrings if op.splitext(op.basename(p))[0] not in excludes]
    for strings_path in allstrings:
        strings2pot(strings_path, dest)

def strings2po(en_strings, tr_strings, dest):
    # This function is a temporary function to get translation information from XIB strings files
    # into .po files. Because XIB strings look like "123.title" = "foobar";, we need the reference
    # english strings file to know what the english title of object 123 actually is. We could rely
    # on the comment just before every entry, but it seems like newlines and other special
    # characters are ommited from the comment, so it messes up our stuff.
    # Once all cocoa strings have been translated and I only receive translations in the new .po
    # format, this function won't be needed anymore.
    # If the strings you're working with is a non-XIB one, pass None in en_strings.
    print("Processing {} with {} onto {}".format(tr_strings, en_strings, dest))
    re_trans = re.compile(r'"(.*)" = "(.*)";')
    with open(tr_strings, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    # ref2tr = {123.title: translated}
    ref2tr = {ref: unescape_cocoa_strings(tr) for ref, tr in re_trans.findall(contents)}
    if en_strings:
        with open(en_strings, 'rt', encoding='utf-8') as fp:
            contents = fp.read()
        # ref2en = {123.title: en}
        ref2en = {ref: unescape_cocoa_strings(en) for ref, en in re_trans.findall(contents)}
    else:
        ref2en = {x: x for x in ref2tr}
    po = polib.pofile(dest)
    print("Untranslated entries: {}".format(len(po.untranslated_entries())))
    count = 0
    for ref, en in ref2en.items():
        translated = ref2tr.get(ref)
        if not translated:
            continue
        entry = po.find(en)
        if entry is None:
            print("WARGNING: {} not found in dest .po".format(en))
            continue
        if entry.msgstr:
            if entry.msgstr != translated:
                print("WARNING: {} != {} for {}".format(translated, entry.msgstr, en))
        else:
            entry.msgstr = translated
            count += 1
    print("Updated {} translations".format(count))
    po.save()

def allstrings2po(enlproj, trlproj, dest, excludes=None):
    allstrings = files_with_ext(trlproj, '.strings')
    for stringsfile in allstrings:
        basename = op.splitext(op.basename(stringsfile))[0]
        if excludes and basename in excludes:
            continue
        enstrings = op.join(enlproj, basename + '.strings')
        strings2po(enstrings, stringsfile, dest)

def po2strings(pofile, en_strings, dest):
    # Takes en_strings and replace all righthand parts of "foo" = "bar"; entries with translations
    # in pofile, then puts the result in dest.
    po = polib.pofile(pofile)
    if not modified_after(pofile, dest):
        return
    print("Creating {} from {}".format(dest, pofile))
    with open(en_strings, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    re_trans = re.compile(r'(?<= = ").*(?=";\n)')
    def repl(match):
        s = match.group(0)
        unescaped = unescape_cocoa_strings(s)
        entry = po.find(unescaped)
        if entry is None:
            print("WARNING: Could not find entry '{}' in .po file".format(s))
            return s
        trans = entry.msgstr
        return escape_cocoa_strings(trans) if trans else s
    contents = re_trans.sub(repl, contents)
    with open(dest, 'wt', encoding='utf-8') as fp:
        fp.write(contents)

def po2allxibstrings(pofile, en_lproj, dest_lproj):
    if not op.exists(dest_lproj):
        os.mkdir(dest_lproj)
    allstrings = all_xib_strings(en_lproj)
    for strings in allstrings:
        deststrings = op.join(dest_lproj, op.basename(strings))
        po2strings(pofile, strings, deststrings)

#--- Qt
def unescape_xml(s):
    return s.replace('&quot;', '"').replace('&apos;', '\'').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

def ts2po(tsfile, dest):
    # This function is a temporary function to get translation information from Qt's ts files.
    print("Processing {} onto {}".format(tsfile, dest))
    re_trans = re.compile(r'<source>(.*?)</source>[\n\r\t ]*?<translation>(.*?)</translation>', re.MULTILINE|re.DOTALL)
    with open(tsfile, 'rt', encoding='utf-8') as fp:
        contents = fp.read()
    # ref2tr = {123.title: translated}
    en2tr = {unescape_xml(en): unescape_xml(tr) for en, tr in re_trans.findall(contents)}
    po = polib.pofile(dest)
    print("Untranslated entries: {}".format(len(po.untranslated_entries())))
    count = 0
    for en, translated in en2tr.items():
        entry = po.find(en)
        if entry is None:
            continue
        if entry.msgstr:
            if entry.msgstr != translated:
                print("WARNING: {} != {} for {}".format(translated, entry.msgstr, en))
        else:
            entry.msgstr = translated
            count += 1
    print("Updated {} translations".format(count))
    po.save()
