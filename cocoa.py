# Created By: Virgil Dupras
# Created On: 2007-10-06
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import time
import traceback
import subprocess
import sys

import objc
from AppKit import *
from ExceptionHandling import NSExceptionHandler, NSLogAndHandleEveryExceptionMask

from .job import Job, JobCancelled, ThreadedJobPerformer as ThreadedJobPerformerBase

def report_crash(type, value, tb):
    mainBundle = NSBundle.mainBundle()
    app_identifier = mainBundle.bundleIdentifier()
    app_version = mainBundle.infoDictionary().get('CFBundleVersion', 'Unknown')
    s = "Application Identifier: {0}".format(app_identifier)
    s += "\nApplication Version: {0}\n\n".format(app_version)
    s += ''.join(traceback.format_exception(type, value, tb))
    HSErrorReportWindow = mainBundle.classNamed_('HSErrorReportWindow')
    if HSErrorReportWindow is None:
        logging.error(s)
        return
    if app_identifier:
        s += '\nRelevant Console logs:\n\n'
        p = subprocess.Popen(['grep', app_identifier, '/var/log/system.log'], stdout=subprocess.PIPE)
        s += p.communicate()[0]
    HSErrorReportWindow.showErrorReportWithContent_(s)

class ThreadedJobPerformer(ThreadedJobPerformerBase):
    def _async_run(self, *args):
        pool = NSAutoreleasePool.alloc().init()
        target = args[0]
        args = tuple(args[1:])
        self._job_running = True
        self._last_error = None
        try:
            target(*args)
        except JobCancelled:
            pass
        except Exception:
            self._last_error = sys.exc_info()
            report_crash(*self._last_error)
        finally:
            self._job_running = False
            self.last_progress = None
            del pool
    

def as_fetch(as_list, as_type, step_size=1000):
    """When fetching items from a very big list through applescript, the connection with the app
    will timeout. This function is to circumvent that. 'as_type' is the type of the items in the 
    list (found in appscript.k). If we don't pass it to the 'each' arg of 'count()', it doesn't work.
    applescript is rather stupid..."""
    result = []
    # no timeout. default timeout is 60 secs, and it is reached for libs > 30k songs
    item_count = as_list.count(each=as_type, timeout=0)
    steps = item_count // step_size
    if item_count % step_size:
        steps += 1
    logging.info('Fetching %d items in %d steps' % (item_count, steps))
    # Don't forget that the indexes are 1-based and that the upper limit is included
    for step in range(steps):
        begin = step * step_size + 1
        end = min(item_count, begin + step_size - 1)
        if end > begin:
            result += as_list[begin:end](timeout=0)
        else: # When there is only one item, the stupid fuck gives it directly instead of putting it in a list.
            result.append(as_list[begin:end](timeout=0))
        time.sleep(.1)
    logging.info('%d items fetched' % len(result))
    return result

def install_exception_hook():
    if '_exceptionHandlerDelegate' in globals():
        # already installed
        return
    def isPythonException(exception):
        return (exception.userInfo() or {}).get(u'__pyobjc_exc_type__') is not None

    class PyObjCExceptionDelegate(NSObject):
        def exceptionHandler_shouldLogException_mask_(self, sender, exception, aMask):
            if exception.name() == 'NSAccessibilityException':
                return False # These kind of exception are really weird and happen all the time with VoiceOver on.
            if isPythonException(exception):
                userInfo = exception.userInfo()
                type = userInfo[u'__pyobjc_exc_type__']
                value = userInfo[u'__pyobjc_exc_value__']
                tb = userInfo.get(u'__pyobjc_exc_traceback__', [])
                report_crash(type, value, tb)
            return True
        exceptionHandler_shouldLogException_mask_ = objc.selector(exceptionHandler_shouldLogException_mask_, signature='c@:@@I')

        def exceptionHandler_shouldHandleException_mask_(self, sender, exception, aMask):
            return False
        exceptionHandler_shouldHandleException_mask_ = objc.selector(exceptionHandler_shouldHandleException_mask_, signature='c@:@@I')

    # we need to retain this, cause the handler doesn't
    global _exceptionHandlerDelegate
    delegate = PyObjCExceptionDelegate.alloc().init()
    NSExceptionHandler.defaultExceptionHandler().setExceptionHandlingMask_(NSLogAndHandleEveryExceptionMask)
    NSExceptionHandler.defaultExceptionHandler().setDelegate_(delegate)
    _exceptionHandlerDelegate = delegate

def pythonify(o):
    """Changes 'o' into a python class (pyobjc_unicode --> u'', NSDictionary --> {}, NSArray --> [])
    """
    if o is None:
        return None
    elif isinstance(o, objc.pyobjc_unicode):
        return unicode(o)
    elif isinstance(o, (objc._pythonify.OC_PythonLong, objc._pythonify.OC_PythonInt)):
        return int(o)
    elif isinstance(o, NSArray):
        return [pythonify(item) for item in o]
    elif isinstance(o, NSDictionary):
        return dict((pythonify(k), pythonify(v)) for k, v in o.items())
    logging.warning('Could not pythonify {0} (of type {1}'.format(repr(o), type(o)))
    return o
