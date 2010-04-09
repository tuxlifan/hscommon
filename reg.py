# Created By: Virgil Dupras
# Created On: 2009-05-16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from hashlib import md5

ALL_APPS = [
    (1, 'dupeGuru Music Edition'),
    (2, 'musicGuru'),
    (4, 'dupeGuru'),
    (5, 'dupeGuru Picture Edition'),
    (6, 'moneyGuru'),
]

class RegistrationRequired(Exception):
    """Registration is required to continue"""

class InvalidCodeError(Exception):
    """The supplied code is invalid."""

class RegistrableApplication(object):
    def __init__(self, appid):
        self.appid = appid
        self.registered = False
        self.register_code = ''
        self.register_email = ''
    
    @staticmethod
    def _is_code_valid(appid, code, email):
        if len(code) != 32:
            return False
        appid = str(appid)
        for i in range(100):
            digest = md5(appid + email + str(i) + 'aybabtu').hexdigest()
            if digest == code:
                return True
        return False
    
    def _setup_as_registered(self):
        pass # virtual
    
    def validate_code(self, code, email):
        DEFAULT_MSG = "Your code is invalid. Make sure that you wrote the good code. Also make sure "\
            "that the e-mail you gave is the same as the e-mail you used for your purchase."
        code = code.strip().lower()
        email = email.strip().lower()
        if self._is_code_valid(self.appid, code, email):
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
    
