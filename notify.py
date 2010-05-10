# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

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
    

class Repeater(Broadcaster, Listener):
    REPEATED_NOTIFICATIONS = None
    
    def __init__(self, broadcaster):
        Broadcaster.__init__(self)
        Listener.__init__(self, broadcaster)
    
    def dispatch(self, msg):
        if hasattr(self, msg):
            Listener.dispatch(self, msg)
        if not self.REPEATED_NOTIFICATIONS or msg in self.REPEATED_NOTIFICATIONS:
            self.notify(msg)
    
