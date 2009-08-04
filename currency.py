# Created By: Virgil Dupras
# Created On: 2008-04-20
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime
import logging
import sqlite3 as sqlite

from . import io
from .path import Path


class Currency(object):
    all = []
    by_code = {}
    by_name = {}
    rates_db = None

    def __new__(cls, code=None, name=None):
        """Returns the currency with the given code."""
        assert (code is None and name is not None) or (code is not None and name is None)
        if code is not None:
            try:
                return cls.by_code[code]
            except KeyError:
                raise ValueError('Unknown currency code: %r' % code)
        else:
            try:
                return cls.by_name[name]
            except KeyError:
                raise ValueError('Unknown currncy name: %r' % name)

    def __getnewargs__(self):
        return (self.code,)
 
    def __getstate__(self):
        return None
  
    def __setstate__(self, state):
        pass

    def __repr__(self):
        return '<Currency %s>' % self.code

    @staticmethod
    def register(code, name, exponent=2, fallback_rate=1):
        """Registers a new currency and returns it."""
        assert code not in Currency.by_code
        assert name not in Currency.by_name
        currency = object.__new__(Currency)
        currency.code = code
        currency.name = name
        currency.exponent = exponent
        currency.fallback_rate = fallback_rate
        Currency.by_code[code] = currency
        Currency.by_name[name] = currency
        Currency.all.append(currency)
        return currency

    @staticmethod
    def set_rates_db(db):
        Currency.rates_db = db

    @staticmethod
    def get_rates_db():
        if Currency.rates_db is None:
            Currency.rates_db = RatesDB()      # Make sure we always have some db to work with
        return Currency.rates_db

    def rates_date_range(self):
        """Returns the range of date for which rates are available for this currency."""
        return self.get_rates_db().date_range(self.code)

    def value_in(self, currency, date):
        """Returns the value of this currency in terms of the other currency on the given date."""
        return self.get_rates_db().get_rate(date, self.code, currency.code)

    def set_CAD_value(self, value, date):
        """Sets the currency's value in CAD on the given date."""
        self.get_rates_db().set_CAD_value(date, self.code, value)


# In order we want to list them
USD = Currency.register('USD', 'U.S. dollar', fallback_rate=0.9896)
EUR = Currency.register('EUR', 'European Euro', fallback_rate=1.5611)
GBP = Currency.register('GBP', 'U.K. pound sterling', fallback_rate=1.9619)
CAD = Currency.register('CAD', 'Canadian dollar', fallback_rate=1)
AUD = Currency.register('AUD', 'Australian dollar', fallback_rate=0.9507)
JPY = Currency.register('JPY', 'Japanese yen', exponent=0, fallback_rate=0.009569)
INR = Currency.register('INR', 'Indian rupee', fallback_rate=0.02322)
NZD = Currency.register('NZD', 'New Zealand dollar', fallback_rate=0.7793)
CHF = Currency.register('CHF', 'Swiss franc', fallback_rate=0.9658)
ZAR = Currency.register('ZAR', 'South African rand', fallback_rate=0.1286)
# The rest, alphabetical
AED = Currency.register('AED', 'U.A.E. dirham', fallback_rate=0.2694)
ANG = Currency.register('ANG', 'Neth. Antilles florin', fallback_rate=0.556)
ARS = Currency.register('ARS', 'Argentine peso', fallback_rate=0.3079)
ATS = Currency.register('ATS', 'Austrian schilling')    # obsolete (euro)
BEF = Currency.register('BEF', 'Belgian franc')   # obsolete (euro)
BRL = Currency.register('BHD', 'Bahraini dinar', fallback_rate=3.1517, exponent=3)
BRL = Currency.register('BRL', 'Brazilian real', fallback_rate=0.5955)
BSD = Currency.register('BSD', 'Bahamian dollar', fallback_rate=0.9896)
CLP = Currency.register('CLP', 'Chilean peso', exponent=0, fallback_rate=0.002082)
CNY = Currency.register('CNY', 'Chinese renminbi', fallback_rate=0.1427)
COP = Currency.register('COP', 'Colombian peso', fallback_rate=0.000557)
CZK = Currency.register('CZK', 'Czech Republic koruna', fallback_rate=0.0622)
DEM = Currency.register('DEM', 'German deutsche mark')   # obsolete (euro)
DKK = Currency.register('DKK', 'Danish krone', fallback_rate=0.2093)
EGP = Currency.register('EGP', 'Egyptian Pound', fallback_rate=0.2232)
ESP = Currency.register('ESP', 'Spanish peseta', exponent=0)   # obsolete (euro)
FIM = Currency.register('FIM', 'Finnish markka')   # obsolete (euro)
FJD = Currency.register('FJD', 'Fiji dollar', fallback_rate=0.6709)
FRF = Currency.register('FRF', 'French franc')     # obsolete (euro)
GHC = Currency.register('GHC', 'Ghanaian cedi (old)') # obsolete
GHS = Currency.register('GHS', 'Ghanaian cedi (new)', fallback_rate=0.974)
GRD = Currency.register('GRD', 'Greek drachma')   # obsolete (euro)
GTQ = Currency.register('GTQ', 'Guatemalan quetzal', fallback_rate=0.1333)
HKD = Currency.register('HKD', 'Hong Kong dollar', fallback_rate=0.126812)
HNL = Currency.register('HNL', 'Honduran lempira', fallback_rate=0.05237)
HRK = Currency.register('HRK', 'Croatian kuna', fallback_rate=0.2151)
HUF = Currency.register('HUF', 'Hungarian forint', fallback_rate=0.006388)
IDR = Currency.register('IDR', 'Indonesian rupiah', fallback_rate=0.000106)
IEP = Currency.register('IEP', 'Irish pound')    # obsolete (euro)
ILS = Currency.register('ILS', 'Israeli new shekel', fallback_rate=0.2987)
ISK = Currency.register('ISK', 'Icelandic krona', exponent=0, fallback_rate=0.01368)
ITL = Currency.register('ITL', 'Italian lira', exponent=0)   # obsolete (euro)
JMD = Currency.register('JMD', 'Jamaican dollar', fallback_rate=0.01413)
KRW = Currency.register('KRW', 'South Korean won', exponent=0, fallback_rate=0.000944)
LKR = Currency.register('LKR', 'Sri Lanka rupee', fallback_rate=0.00919)
MAD = Currency.register('MAD', 'Moroccan dirham', fallback_rate=0.136)
MMK = Currency.register('MMK', 'Myanmar (Burma) kyat')
MXN = Currency.register('MXN', 'Mexican peso', fallback_rate=0.0953)
MYR = Currency.register('MYR', 'Malaysian ringgit', fallback_rate=0.3064)
NLG = Currency.register('NLG', 'Netherlands guilder')   # obsolete (euro)
NOK = Currency.register('NOK', 'Norwegian krone', fallback_rate=0.1973)
PAB = Currency.register('PAB', 'Panamanian balboa', fallback_rate=0.9896)
PEN = Currency.register('PEN', 'Peruvian new sol', fallback_rate=0.3481)
PHP = Currency.register('PHP', 'Philippine peso', fallback_rate=0.02273)
PKR = Currency.register('PKR', 'Pakistan rupee', fallback_rate=0.01454)
PLN = Currency.register('PLN', 'Polish zloty', fallback_rate=0.4601)
PTE = Currency.register('PTE', 'Portuguese escudo', exponent=0)    # obsolete (euro)
RON = Currency.register('RON', 'Romanian new leu', fallback_rate=0.4254)
RSD = Currency.register('RSD', 'Serbian dinar', fallback_rate=0.01912)
RUB = Currency.register('RUB', 'Russian rouble', fallback_rate=0.04206)
SEK = Currency.register('SEK', 'Swedish krona', fallback_rate=0.1676)
SGD = Currency.register('SGD', 'Singapore dollar', fallback_rate=0.7266)
SIT = Currency.register('SIT', 'Slovenian tolar')     # obsolete (euro)
SKK = Currency.register('SKK', 'Slovak koruna', fallback_rate=0.05015)
THB = Currency.register('THB', 'Thai baht', fallback_rate=0.03079)
TND = Currency.register('TND', 'Tunisian dinar', exponent=3, fallback_rate=0.8516)
TRL = Currency.register('TRL', 'Turkish lira', exponent=0)       # obsolete
TWD = Currency.register('TWD', 'Taiwanese new dollar', fallback_rate=0.03246)
VEB = Currency.register('VEB', 'Venezuelan bolivar', exponent=0)    # obsolete
VEF = Currency.register('VEF', 'Venezuelan bolivar fuerte', fallback_rate=0.4609)
VND = Currency.register('VND', 'Vietnamese dong', fallback_rate=6.1e-05)
XAF = Currency.register('XAF', 'CFA franc', exponent=0, fallback_rate=0.00238)
XCD = Currency.register('XCD', 'East Caribbean dollar', fallback_rate=0.3734)
XPF = Currency.register('XPF', 'CFP franc', exponent=0, fallback_rate=0.01308)


class RatesDB(object):
    """Stores exchange rates for currencies.
    
    The currencies are identified with ISO 4217 code (USD, CAD, EUR, etc.).
    The rates are represented as float and represent the value of the currency in CAD.
    """
    def __init__(self, db_or_path=':memory:'):
        self.db_or_path = db_or_path
        if isinstance(db_or_path, (basestring, Path)):
            self.con = sqlite.connect(unicode(db_or_path))
        else:
            self.con = db_or_path
        self._execute("select * from rates where 1=2")
    
    def _execute(self, *args, **kwargs):
        def create_tables():
            # date is stored as a TEXT YYYYMMDD
            sql = "create table rates(date TEXT, currency TEXT, rate REAL NOT NULL)"
            self.con.execute(sql)
            sql = "create unique index idx_rate on rates (date, currency)"
            self.con.execute(sql)
        
        try:
            return self.con.execute(*args, **kwargs)
        except sqlite.OperationalError: # new db, or other problems
            try:
                create_tables()
            except Exception:
                logging.warning("Messy problems with the currency db, starting anew with a memory db")
                self.con = sqlite.connect(':memory:')
                create_tables()
        except sqlite.DatabaseError: # corrupt db
            logging.warning("Corrupt currency database at {0}. Starting over.".format(repr(self.db_or_path)))
            if isinstance(self.db_or_path, (basestring, Path)):
                self.con.close()
                io.remove(Path(self.db_or_path))
                self.con = sqlite.connect(unicode(self.db_or_path))
            else:
                logging.warning("Can't re-use the file, using a memory table")
                self.con = sqlite.connect(':memory:')
            create_tables()
        return self.con.execute(*args, **kwargs) # try again
    
    def _seek_value_in_CAD(self, str_date, currency_code):
        if currency_code == 'CAD':
            return 1
        def seek(date_op, desc):
            sql = "select rate from rates where date %s ? and currency = ? order by date %s limit 1" % (date_op, desc)
            cur = self._execute(sql, [str_date, currency_code])
            row = cur.fetchone()
            if row:
                return row[0]
        return seek('<=', 'desc') or seek('>=', '') or Currency(currency_code).fallback_rate
    
    def date_range(self, currency_code):
        """Returns (start, end) of the cached rates for currency"""
        sql = "select min(date), max(date) from rates where currency = '%s'" % currency_code
        cur = self._execute(sql)
        start, end = cur.fetchone()
        if start and end:
            convert = lambda s: datetime.datetime.strptime(s, '%Y%m%d').date()
            return convert(start), convert(end)
        else:
            return None
    
    def get_rate(self, date, currency1_code, currency2_code):
        """Returns the exchange rate between currency1 and currency2 for date.
        
        The rate returned means '1 unit of currency1 is worth X units of currency2'.
        The rate of the nearest date that is smaller than 'date' is returned. If
        there is none, a seek for a rate with a higher date will be made.
        """
        str_date = '%d%02d%02d' % (date.year, date.month, date.day)
        value1 = self._seek_value_in_CAD(str_date, currency1_code)
        value2 = self._seek_value_in_CAD(str_date, currency2_code)
        return value1 / value2
    
    def set_CAD_value(self, date, currency_code, value):
        """Sets the daily value in CAD for currency at date"""
        str_date = '%d%02d%02d' % (date.year, date.month, date.day)
        sql = "replace into rates(date, currency, rate) values(?, ?, ?)"
        self._execute(sql, [str_date, currency_code, value])
        self.con.commit()
