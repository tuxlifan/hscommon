# Created By: Virgil Dupras
# Created On: 2009-05-16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from hashlib import md5
import json
from urllib.request import urlopen, URLError
import logging
import socket

ALL_APPS = [
    (1, 'dupeGuru'),
    (2, 'moneyGuru'),
    (3, 'musicGuru'),
]

OLDAPPIDS = {
    1: {1, 4, 5},
    2: {6, },
    3: {2, },
}

class InvalidCodeError(Exception):
    """The supplied code is invalid."""

class RegistrableApplication(object):
    def __init__(self, appid):
        self.appid = appid
        self.registered = False
        self.register_code = ''
        self.register_email = ''
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
    
    def _setup_as_registered(self):
        pass # virtual
    
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
    
    def set_registration(self, code, email):
        try:
            self.validate_code(code, email)
            self.registration_code = code
            self.registration_email = email
            self.registered = True
            self._setup_as_registered()
        except InvalidCodeError:
            pass
    
    @property
    def unpaid_hours(self):
        if self._unpaid_hours is None:
            url = 'http://open.hardcoded.net/backend/unpaid/{0}'.format(self.appid)
            try:
                connection = urlopen(url)
                response = str(connection.read(), 'latin-1')
                self._unpaid_hours = json.loads(response)
                connection.close()
            except (URLError, socket.error, ValueError): # ValueError is for json.loads()
                logging.warning("Couldn't connect to open.hardcoded.net")
                self._unpaid_hours = 0
        return self._unpaid_hours
    
