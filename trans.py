# Created By: Virgil Dupras
# Created On: 2010-06-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# Doing i18n with GNU gettext for the core text gets complicated, so what I do is that I make the
# GUI layer responsible for supplying a tr() function.

_trfunc = None

def tr(s, context=None):
    if _trfunc is None:
        return s
    else:
        if context:
            return _trfunc(s, context)
        else:
            return _trfunc(s)

def set_tr(new_tr):
    global _trfunc
    _trfunc = new_tr

def install_cocoa_trans():
    from .cocoa.objcmin import NSBundle
    mainBundle = NSBundle.mainBundle()
    def cocoa_tr(s, context='core'):
        return mainBundle.localizedStringForKey_value_table_(s, s, context)
    set_tr(cocoa_tr)
    currentLang = NSBundle.preferredLocalizationsFromArray_(mainBundle.localizations())[0]
    LANG2LOCALENAME = {'fr': 'fr_FR', 'de': 'de_DE'}
    if currentLang in LANG2LOCALENAME:
        import locale
        locale.setlocale(locale.LC_ALL, LANG2LOCALENAME[currentLang])
