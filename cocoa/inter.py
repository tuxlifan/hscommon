# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# Interfaces for proxies in cocoalib

import logging

import objc

from ..reg import InvalidCodeError
from .objcmin import NSObject

if objc.__version__ == '1.4':
    # we're 32 bit and the _C_NSInteger and _C_CGFloat consts aint there.
    signature = objc.signature
else:
    def signature(signature):
        """Returns an objc.signature with 'i' and 'f' letters changed to correct NSInteger and
        CGFloat values.
        """
        signature = signature.replace('i', objc._C_NSInteger)
        signature = signature.replace('I', objc._C_NSUInteger)
        signature = signature.replace('f', objc._C_CGFloat)
        return objc.signature(signature)

class PyGUIObject(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        super(PyGUIObject, self).init()
        self.cocoa = cocoa
        self.py = self.py_class(self, pyparent.py)
        return self
    
    def connect(self):
        if hasattr(self.py, 'connect'):
            self.py.connect()
    
    def disconnect(self):
        if hasattr(self.py, 'disconnect'):
            self.py.disconnect()
    
    def free(self):
        # call this method only when you don't need to use this proxy anymore. you need to call this
        # if you want to release the cocoa side (self.cocoa is holding a refcount)
        # We don't delete py, it might be called after the free. It will be garbage collected anyway.
        # The if is because there is something happening giving a new ref to cocoa right after
        # the free, and then the ref gets to 1 again, free is called again.
        self.disconnect()
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    #--- Python -> Cocoa
    def refresh(self):
        self.cocoa.refresh()
    

class PyOutline(PyGUIObject):
    def cancelEdits(self):
        self.py.cancel_edits()
    
    @signature('c@:@@')
    def canEditProperty_atPath_(self, propname, path):
        node = self.py.get_node(path)
        assert node is self.py.selected_node
        return getattr(node, 'can_edit_' + propname, False)
    
    def saveEdits(self):
        self.py.save_edits()
    
    def selectedPath(self):
        return self.py.selected_path
    
    def setSelectedPath_(self, path):
        self.py.selected_path = path
    
    def selectedPaths(self):
        return self.py.selected_paths

    def setSelectedPaths_(self, paths):
        self.py.selected_paths = paths

    def property_valueAtPath_(self, property, path):
        try:
            return getattr(self.py.get_node(path), property)
        except IndexError:
            logging.warning(u"%r doesn't have a node at path %r", self.py, path)
            return u''
    
    def setProperty_value_atPath_(self, property, value, path):
        setattr(self.py.get_node(path), property, value)
    
    #--- Python -> Cocoa
    def start_editing(self):
        self.cocoa.startEditing()
    
    def stop_editing(self):
        self.cocoa.stopEditing()
    
    def update_selection(self):
        self.cocoa.updateSelection()
    

class PyRegistrable(NSObject):
    def appName(self):
        return ""
    
    def demoLimitDescription(self):
        return self.py.DEMO_LIMIT_DESC
    
    @signature('c@:')
    def isRegistered(self):
        return self.py.registered
    
    def isCodeValid_withEmail_(self, code, email):
        try:
            self.py.validate_code(code, email)
            return None
        except InvalidCodeError as e:
            return unicode(e)
    
    def setRegisteredCode_andEmail_(self, code, email):
        self.py.set_registration(code, email)
    
