# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

class Broadcaster(object):
    def __init__(self):
        self.listeners = set()
    
    def add_listener(self, listener):
        self.listeners.add(listener)
    
    def notify(self, msg):
        for listener in self.listeners.copy(): # listeners can change during iteration
            if listener in self.listeners: # disconnected during notification
                listener.dispatch(msg)
    
    def remove_listener(self, listener):
        self.listeners.discard(listener)
    

class Listener(object):
    def __init__(self, broadcaster):
        self.broadcaster = broadcaster
    
    def connect(self):
        self.broadcaster.add_listener(self)
    
    def disconnect(self):
        self.broadcaster.remove_listener(self)
    
    def dispatch(self, msg):
        method = getattr(self, msg)
        method()
    
