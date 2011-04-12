# Created By: Virgil Dupras
# Created On: 2010-06-23
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# Doing i18n with GNU gettext for the core text gets complicated, so what I do is that I make the
# GUI layer responsible for supplying a tr() function.

import sys
import locale
import logging

_trfunc = None

def tr(s, context=None):
    if _trfunc is None:
        return s
    else:
        if context:
            return _trfunc(s, context)
        else:
            return _trfunc(s)

def trmsg(s, context='message'):
    # Long messages in HS translations are referred to by identifiers (SomethingMsg). We really don't
    # want to not have an entry for them in the language database, so if the trfunc returns the same
    # string, we log a warning.
    result = tr(s, context)
    if result == s:
        logging.warning("Message '{}' couldn't be found in the translation database.".format(s))
    return result

def set_tr(new_tr):
    global _trfunc
    _trfunc = new_tr

def get_locale_name(lang):
    if sys.platform == 'win32':
        LANG2LOCALENAME = {'fr': 'fra_fra', 'de': 'deu_deu', 'it': 'ita_ita'}
    else:
        LANG2LOCALENAME = {'fr': 'fr_FR', 'de': 'de_DE', 'it': 'it_IT'}
    if lang not in LANG2LOCALENAME:
        return None
    result = LANG2LOCALENAME[lang]
    if sys.platform == 'linux2':
        result += '.UTF-8'
    return result

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
