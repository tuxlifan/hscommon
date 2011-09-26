# Created By: Virgil Dupras
# Created On: 2009-05-16
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import re
from hashlib import md5
import json
from urllib.request import urlopen, URLError
from urllib.parse import urlencode
from http.client import HTTPException
import logging
import socket

from .trans import trmsg

ALL_APPS = [
    (1, 'dupeGuru'),
    (2, 'moneyGuru'),
    (3, 'musicGuru'),
    (6, 'PdfMasher'),
]

OLDAPPIDS = {
    1: {1, 4, 5},
    2: {6, },
    3: {2, },
}

class InvalidCodeError(Exception):
    """The supplied code is invalid."""

# At the moment, the translations for FairwarePromptMsg and DemoPromptMsg are in each application's
# message trans files, which means that there's needless duplication. At some point, I'll have to
# implement a way to automatically merge a central trans file with another at build time to reduce
# that duplication.

class RegistrableApplication:
    #--- View interface
    # get_default(key_name)
    # set_default(key_name, value)
    # setup_as_registered()
    # show_message(msg)
    # show_fairware_nag(prompt)
    # show_demo_nag(prompt)
    # open_url(url)
    
    PROMPT_NAME = "<undefined>"
    DEMO_LIMITATION = "<undefined>"
    
    def __init__(self, view, appid):
        self.view = view
        self.appid = appid
        self.registered = False
        self.fairware_mode = False
        self.registration_code = ''
        self.registration_email = ''
        self._unpaid_hours = None
    
    @staticmethod
    def _is_code_valid(appid, code, email):
        if len(code) != 32:
            return False
        appid = str(appid)
        for i in range(100):
            blob = appid + email + str(i) + 'aybabtu'
            digest = md5(blob.encode('utf-8')).hexdigest()
            if digest == code:
                return True
        return False
    
    def _set_registration(self, code, email):
        self.validate_code(code, email)
        self.registration_code = code
        self.registration_email = email
        self.registered = True
        self.view.setup_as_registered()
    
    def initial_registration_setup(self):
        # Should be called only after the app is finished launching
        code = self.view.get_default('RegistrationCode')
        email = self.view.get_default('RegistrationEmail')
        if code and email:
            try:
                self._set_registration(code, email)
            except InvalidCodeError:
                pass
        if not self.registered:
            if self.view.get_default('FairwareMode'):
                self.fairware_mode = True
            if self.fairware_mode:
                if self.should_show_fairware_reminder:
                    prompt = trmsg('FairwarePromptMsg').format(name=self.PROMPT_NAME)
                    self.view.show_fairware_nag(prompt)
            else:
                prompt = trmsg('DemoPromptMsg').format(name=self.PROMPT_NAME, limitation=self.DEMO_LIMITATION)
                self.view.show_demo_nag(prompt)
    
    def validate_code(self, code, email):
        code = code.strip().lower()
        email = email.strip().lower()
        if self._is_code_valid(self.appid, code, email):
            return
        # Check if it's not an old reg code
        for oldappid in OLDAPPIDS.get(self.appid, []):
            if self._is_code_valid(oldappid, code, email):
                return
        # let's see if the user didn't mix the fields up
        if self._is_code_valid(self.appid, email, code):
            msg = "Invalid Code. It seems like you inverted the 'Registration Code' and"\
                "'Registration E-mail' field."
            raise InvalidCodeError(msg)
        # Is the code a paypal transaction id?
        if re.match(r'^[a-z\d]{17}$', code) is not None:
            msg = "The code you submitted looks like a Paypal transaction ID. Registration codes are "\
                "32 digits codes which you should have received in a separate e-mail. If you haven't "\
                "received it yet, please visit http://www.hardcoded.net/support/"
            raise InvalidCodeError(msg)
        # Invalid, let's see if it's a code for another app.
        for appid, appname in ALL_APPS:
            if self._is_code_valid(appid, code, email):
                msg = "This code is a {0} code. You're running the wrong application. You can "\
                    "download the correct application at http://www.hardcoded.net".format(appname)
                raise InvalidCodeError(msg)
        DEFAULT_MSG = "Your code is invalid. Make sure that you wrote the good code. Also make sure "\
            "that the e-mail you gave is the same as the e-mail you used for your purchase."
        raise InvalidCodeError(DEFAULT_MSG)
    
    def set_registration(self, code, email, register_os):
        if not self.fairware_mode and 'fairware' in {code.strip().lower(), email.strip().lower()}:
            self.fairware_mode = True
            self.view.set_default('FairwareMode', True)
            self.view.show_message("Fairware mode enabled.")
            return True
        try:
            self._set_registration(code, email)
            self.view.show_message("Your code is valid. Thanks!")
            if register_os:
                self.register_os()
            self.view.set_default('RegistrationCode', self.registration_code)
            self.view.set_default('RegistrationEmail', self.registration_email)
            return True
        except InvalidCodeError as e:
            self.view.show_message(str(e))
            return False
    
    def register_os(self):
        if not self.registered:
            return
        url = 'http://open.hardcoded.net/backend/register/'
        data = {'email': self.registration_email, 'osname': sys.platform}
        encoded = bytes(urlencode(data), encoding='ascii')
        try:
            urlopen(url, data=encoded)
        except URLError:
            pass
    
    def contribute(self):
        self.view.open_url("http://open.hardcoded.net/contribute/")
    
    def buy(self):
        self.view.open_url("http://www.hardcoded.net/purchase.htm")
    
    def about_fairware(self):
        self.view.open_url("http://open.hardcoded.net/about/")
    
    @property
    def should_show_fairware_reminder(self):
        return (not self.registered) and (self.fairware_mode) and (self.unpaid_hours >= 1)
    
    @property
    def should_apply_demo_limitation(self):
        return (not self.registered) and (not self.fairware_mode)
    
    @property
    def unpaid_hours(self):
        if self._unpaid_hours is None:
            url = 'http://open.hardcoded.net/backend/unpaid/{}'.format(self.appid)
            try:
                # The timeout is there to avoid delaying the launching of the app too much. Ideally,
                # this operation should be async, but that's for another time.
                # XXX Make unpaid hours fetching (and display of fairware dialog) async.
                connection = urlopen(url, timeout=5)
                response = str(connection.read(), 'latin-1')
                self._unpaid_hours = json.loads(response)
                connection.close()
            except (URLError, HTTPException, socket.error, ValueError): # ValueError is for json.loads()
                logging.warning("Couldn't connect to open.hardcoded.net")
                self._unpaid_hours = 0
        return self._unpaid_hours
    
