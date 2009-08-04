# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from ..testcase import TestCase
from ..notify import Broadcaster, Listener

class HelloListener(Listener):
    def __init__(self, broadcaster):
        Listener.__init__(self, broadcaster)
        self.hello_count = 0

    def hello(self):
        self.hello_count += 1

class NoSetUp(TestCase):
    def test_disconnect_during_notification(self):
        """When a listener disconnects another listener the other listener will not receive a 
        notification.
        """
        # This whole complication scheme below is because the order of the notification is not
        # guaranteed. We could disconnect everything from self.broadcaster.listeners, but this
        # member is supposed to be private. Hence, the '.other' scheme
        class Disconnecter(Listener):
            def __init__(self, broadcaster):
                Listener.__init__(self, broadcaster)
                self.hello_count = 0
            
            def hello(self):
                self.hello_count += 1
                self.other.disconnect()
            
        broadcaster = Broadcaster()
        first = Disconnecter(broadcaster)
        second = Disconnecter(broadcaster)
        first.other, second.other = second, first
        first.connect()
        second.connect()
        broadcaster.notify('hello')
        # only one of them was notified
        self.assertEqual(first.hello_count + second.hello_count, 1)
    
class NotifyTest(TestCase):
    def setUp(self):
        self.broadcaster = Broadcaster()
        self.listener = HelloListener(self.broadcaster)

    def test_disconnect(self):
        """After a disconnect, the listener doesn't hear anything"""
        self.listener.connect()
        self.listener.disconnect()
        self.broadcaster.notify('hello')
        self.assertEqual(self.listener.hello_count, 0)
    
    def test_disconnect_when_not_connected(self):
        """When disconnecting an already disconnected listener, nothing happens"""
        self.listener.disconnect()
    
    def test_not_connected_on_init(self):
        """A listener is not initialized connected"""
        self.broadcaster.notify('hello')
        self.assertEqual(self.listener.hello_count, 0)
    
    def test_notify(self):
        """The listener listens to the broadcaster."""
        self.listener.connect()
        self.broadcaster.notify('hello')
        self.assertEqual(self.listener.hello_count, 1)
    
    def test_reconnect(self):
        """It's possible to reconnect a listener after disconnection"""
        self.listener.connect()
        self.listener.disconnect()
        self.listener.connect()
        self.broadcaster.notify('hello')
        self.assertEqual(self.listener.hello_count, 1)
    
