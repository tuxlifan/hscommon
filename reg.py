# Created By: Virgil Dupras
# Created On: 2009-05-16
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from hashlib import md5

class RegistrationRequired(Exception):
    """Registration is required to continue"""

class RegistrableApplication(object):
    def __init__(self, appid):
        self.appid = appid
        self.registered = False
        self.register_code = ''
        self.register_email = ''
    
    def _setup_as_registered(self):
        pass # virtual
    
    def is_code_valid(self, code, email):
        appid = str(self.appid)
        code = code.strip().lower()
        email = email.strip().lower()
        if len(code) != 32:
            return False
        for i in range(100):
            digest = md5(appid + email + str(i) + 'aybabtu').hexdigest()
            if digest == code:
                return True
        return False
    
    def set_registration(self, code, email):
        if self.is_code_valid(code, email):
            self.registration_code = code
            self.registration_email = email
            self.registered = True
            self._setup_as_registered()
    
