# Created By: Virgil Dupras
# Created On: 2010-06-23
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# Doing i18n with GNU gettext for the core text gets complicated, so what I do is that I make the
# GUI layer responsible for supplying a tr() function.

import locale
import logging
import os.path as op

from .plat import ISWINDOWS, ISLINUX

_trfunc = None
_trget = None

def tr(s, context=None):
    if _trfunc is None:
        return s
    else:
        if context:
            return _trfunc(s, context)
        else:
            return _trfunc(s)

def trget(domain):
    # Returns a tr() function for the specified domain.
    if _trget is None:
        return lambda s: tr(s, domain)
    else:
        return _trget(domain)

def set_tr(new_tr, new_trget=None):
    global _trfunc, _trget
    _trfunc = new_tr
    if new_trget is not None:
        _trget = new_trget

def get_locale_name(lang):
    if ISWINDOWS:
        # http://msdn.microsoft.com/en-us/library/39cwe7zf(vs.71).aspx
        LANG2LOCALENAME = {'fr': 'fra', 'de': 'deu', 'it': 'ita', 'zh_CN': 'chs', 'cs': 'czy',
            'nl': 'nld'}
    else:
        LANG2LOCALENAME = {'fr': 'fr_FR', 'de': 'de_DE', 'it': 'it_IT', 'zh_CN': 'zh_CN',
            'cs': 'cs_CZ', 'nl': 'nl_NL'}
    if lang not in LANG2LOCALENAME:
        return None
    result = LANG2LOCALENAME[lang]
    if ISLINUX:
        result += '.UTF-8'
    return result

#--- Cocoa
def install_cocoa_trans():
    from .cocoa.objcmin import NSBundle
    mainBundle = NSBundle.mainBundle()
    def cocoa_tr(s, context='core'):
        return mainBundle.localizedStringForKey_value_table_(s, s, context)
    set_tr(cocoa_tr)
    currentLang = NSBundle.preferredLocalizationsFromArray_(mainBundle.localizations())[0]
    localename = get_locale_name(currentLang)
    if localename is not None:
        locale.setlocale(locale.LC_ALL, localename)

#--- Qt
def install_qt_trans(lang=None):
    from PyQt4.QtCore import QCoreApplication, QTranslator, QLocale
    if not lang:
        lang = str(QLocale.system().name())[:2]
    localename = get_locale_name(lang)
    if localename is not None:
        try:
            locale.setlocale(locale.LC_ALL, localename)
        except locale.Error:
            logging.warning("Couldn't set locale %s", localename)
    else:
        lang = 'en'
    qtr1 = QTranslator(QCoreApplication.instance())
    qtr1.load(':/qt_%s' % lang)
    QCoreApplication.installTranslator(qtr1)
    qtr2 = QTranslator(QCoreApplication.instance())
    qtr2.load(':/%s' % lang)
    QCoreApplication.installTranslator(qtr2)
    def qt_tr(s, context='core'):
        return str(QCoreApplication.translate(context, s, None))
    set_tr(qt_tr)

#--- gettext
def install_gettext_trans(base_folder, lang):
    import gettext
    def gettext_trget(domain):
        if not lang:
            return lambda s: s
        try:
            return gettext.translation(domain, localedir=base_folder, languages=[lang]).gettext
        except IOError:
            return lambda s: s
    
    default_gettext = gettext_trget('core')
    def gettext_tr(s, context=None):
        if not context:
            return default_gettext(s)
        else:
            trfunc = gettext_trget(context)
            return trfunc(s)
    set_tr(gettext_tr, gettext_trget)

def install_gettext_trans_under_cocoa():
    from .cocoa.objcmin import NSBundle
    mainBundle = NSBundle.mainBundle()
    resFolder = mainBundle.resourceURL().path()
    baseFolder = op.join(resFolder, 'locale')
    currentLang = NSBundle.preferredLocalizationsFromArray_(mainBundle.localizations())[0]
    install_gettext_trans(baseFolder, currentLang)
    localename = get_locale_name(currentLang)
    if localename is not None:
        locale.setlocale(locale.LC_ALL, localename)

def install_gettext_trans_under_qt(base_folder, lang=None):
    # So, we install the gettext locale, great, but we also should try to install qt_*.qm if
    # available so that strings that are inside Qt itself over which I have no control are in the
    # right language.
    from PyQt4.QtCore import QCoreApplication, QTranslator, QLocale
    if not lang:
        lang = str(QLocale.system().name())[:2]
    localename = get_locale_name(lang)
    if localename is not None:
        try:
            locale.setlocale(locale.LC_ALL, localename)
        except locale.Error:
            logging.warning("Couldn't set locale %s", localename)
    else:
        lang = 'en'
    qtr = QTranslator(QCoreApplication.instance())
    qtr.load(':/qt_%s' % lang)
    QCoreApplication.installTranslator(qtr)
    install_gettext_trans(base_folder, lang)
