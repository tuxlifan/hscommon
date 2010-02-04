# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# HS applications use very few Obj-C classes on the python side. However, when using Foundation or
# AppKit directly, all metadata is loaded in memory. In HS case, that means that a lot of memory is
# wasted. This is why this unit exists. It loads up metadata used in HS app manually to minimize
# memory usage.

import objc

foundation_bundle = objc.loadBundle(
        'Foundation',
        globals(),
        bundle_identifier=u'com.apple.Foundation',
)
appkit_bundle = objc.loadBundle(
        'AppKit',
        globals(),
        bundle_path=u'/System/Library/Frameworks/AppKit.framework',
)
exceptionhandling_bundle = objc.loadBundle(
        'ExceptionHandling',
        globals(),
        bundle_path=u'/System/Library/Frameworks/ExceptionHandling.framework',
)

#--- Classes
NSObject = objc.lookUpClass('NSObject')
NSNotificationCenter = objc.lookUpClass('NSNotificationCenter')
NSUserDefaults = objc.lookUpClass('NSUserDefaults')
NSURL = objc.lookUpClass('NSURL')
NSBundle = objc.lookUpClass('NSBundle')
NSAutoreleasePool = objc.lookUpClass('NSAutoreleasePool')
NSArray = objc.lookUpClass('NSArray')
NSDictionary = objc.lookUpClass('NSDictionary')

NSWorkspace = objc.lookUpClass('NSWorkspace')
objc.registerMetaDataForSelector('NSWorkspace', 'performFileOperation:source:destination:files:tag:',
    {
        'retval': {'type': objc._C_NSBOOL},
        'arguments': {
            2+4: {'type_modifier': objc._C_OUT,}
        }
    })
objc.registerMetaDataForSelector('NSWorkspace', 'typeOfFile:error:',
    {
        'arguments': {
            2+1: {'type_modifier': objc._C_OUT,}
        }
    })

NSExceptionHandler = objc.lookUpClass('NSExceptionHandler')
objc.registerMetaDataForSelector('NSExceptionHandler', 'setExceptionHandlingMask:',
    {
        'arguments': {
            2+0: {'type': objc._C_UINT,}
        }
    })

#--- Functions

def S(*args):
    return ''.join(args)

FUNCTIONS = [
    (u'NSSearchPathForDirectoriesInDomains', S('@', objc._C_NSUInteger, objc._C_NSUInteger, 'Z')),
]

objc.loadBundleFunctions(foundation_bundle, globals(), FUNCTIONS)

#--- Constants
# I haven't figured out how to load consts/enums, so I set them manually

NSApplicationSupportDirectory = 14
NSUserDomainMask = 1
NSWorkspaceRecycleOperation = 'recycle'
NSLogAndHandleEveryExceptionMask = 0x3ff