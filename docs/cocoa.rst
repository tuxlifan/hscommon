================================
:mod:`cocoa` - OS X specific lib
================================

This module contain a few hacks, workaround and utilities, mostly for use with PyObjC.

.. function:: install_exception_hook()

    If you call this when your app is running, a hook will be placed in Cocoa's exception handling system and whenever an uncaught exception is raised, a dialog (``HSErrorReportWindow``, it must be present in your main bundle. It's in `cocoalib <http://hg.hardcoded.net/cocoalib>`_ ) will pop up with the traceback, allowing the user to send it to HS support.

.. class:: ThreadedJobPerformer

    This is a subclass of ``job.ThreadedJobPerformer`` that wraps a ``NSAutoreleasePool`` around the async run.

.. function:: as_fetch(as_list, as_type, step_size=1000)

    This is a workaround `appscript`` funkiness. When you ask for a large list of objects through ``appscript``, it can take a long time and end up choking (connection timeout and stuff). This functions fetches items in small steps and return the items in a normal python list. ``as_list`` is the appscript list, ``as_type`` is the type of items in the list (found in ``appscript.k``) and ``step_size`` is the number of items fetched in each pass.

The :mod:`cocoa.inter` submodule
================================

HS applications embed Python code in a pure Objective-C app through PyObjC (I wrote an `article  about this <http://www.hardcoded.net/articles/embedded-pyobjc.htm>`_). This means that each app has an interface unit that converts calls with Objective-C conventions to calls with Python conventions. There are a few of these interfaces that come back in more than one app. To avoid repeating them, I put them in this unit.

The :mod:`cocoa.objcmin` submodule
==================================

Doing stuff like ``import AppKit`` or ``import Foundation`` with PyObjC consumes a lot of memory because it parses all available classes' metadata and keep them in memory. When embedding PyObjC, apps need to use a lot less of that metadata. To save memory usage, I looked at all Objective-C classes and methods I was using in all HS Python code and I manually defined metadata for those in this module. This way, a lot less memory is used. So, instead of doing ``from Foundation import NSObject``, in HS app we must do ``from hscommon.cocoa.objcmin import NSObject``

