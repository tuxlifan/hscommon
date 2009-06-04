# Unit Name: hsutil.currency_test
# Created By: Virgil Dupras
# Created On: 2008-04-20
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from __future__ import division

import copy
import pickle
from datetime import date
import sqlite3 as sqlite

from .. import testcase, io
from ..path import Path
from ..currency import Currency, RatesDB, CAD, EUR, PLN, USD


class TestCase(testcase.TestCase):
    def tearDown(self):
        Currency.set_rates_db(None)


class CurrencyTest(TestCase):
    def test_creation(self):
        """Different ways to create a currency."""
        self.assertEqual(Currency('CAD'), CAD)
        self.assertEqual(Currency(name='Canadian dollar'), CAD)

    def test_copy(self):
        """Currencies can be copied."""
        self.assertEqual(copy.copy(CAD), CAD)
        self.assertEqual(copy.deepcopy(CAD), CAD)


class EmptyMemoryDB(TestCase):
    def test_get_rate(self):
        """When there is no data available, use the fallback rate"""
        self.assertEqual(CAD.value_in(USD, date(2008, 4, 20)), 1 / USD.fallback_rate)
    

class DBWithDailyRate(TestCase):
    def setUp(self):
        USD.set_CAD_value(1/0.996115, date(2008, 4, 20))
    
    def test_get_rate(self):
        """Getting the rate exactly as set_rate happened returns the same rate"""
        self.assertAlmostEqual(CAD.value_in(USD, date(2008, 4, 20)), 0.996115)
    
    def test_get_rate_different_currency(self):
        """Use fallback rates when necessary"""
        self.assertEqual(CAD.value_in(EUR, date(2008, 4, 20)), 1 / EUR.fallback_rate)
        self.assertEqual(EUR.value_in(USD, date(2008, 4, 20)), EUR.fallback_rate * 0.996115)
    
    def test_get_rate_reverse(self):
        """It's possible to get the reverse value of a rate using the same data"""
        self.assertAlmostEqual(USD.value_in(CAD, date(2008, 4, 20)), 1 / 0.996115)
    
    def test_set_rate_twice(self):
        """When setting a rate for an index that already exists, the old rate is replaced by the new"""
        USD.set_CAD_value(1/42, date(2008, 4, 20))
        self.assertAlmostEqual(CAD.value_in(USD, date(2008, 4, 20)), 42)
    

class DBWithTwoDailyRates(TestCase):
    def setUp(self):
        # Don't change the set order, it's important for the tests
        USD.set_CAD_value(1/0.997115, date(2008, 4, 25))
        USD.set_CAD_value(1/0.996115, date(2008, 4, 20))
    
    def test_date_range_range(self):
        """USD.rates_date_range() returns the USD's limits"""
        self.assertEqual(USD.rates_date_range(), (date(2008, 4, 20), date(2008, 4, 25)))
    
    def test_date_range_for_unfetched_currency(self):
        """If the curency is not in the DB, return None"""
        self.assertTrue(PLN.rates_date_range() is None)
    
    def test_seek_rate_middle(self):
        """A rate request with seek in the middle will return the lowest date"""
        self.assertEqual(USD.value_in(CAD, date(2008, 4, 24)), 1/0.996115)
    
    def test_seek_rate_after(self):
        """Make sure that the *nearest* lowest rate is returned. Because the 25th have been set 
        before the 20th, an order by clause is required in the seek SQL to make this test pass"""
        self.assertEqual(USD.value_in(CAD, date(2008, 4, 26)), 1/0.997115)
    
    def test_seek_rate_before(self):
        """If there are no rate in the past, seek for a rate in the future"""
        self.assertEqual(USD.value_in(CAD, date(2008, 4, 19)), 1/0.996115)
    

class DBWithMutlipleCurrencies(TestCase):
    def setUp(self):
        USD.set_CAD_value(1/0.996115, date(2008, 4, 20))
        EUR.set_CAD_value(1/0.633141, date(2008, 4, 20))
    
    def test_get_rate(self):
        """Don't mix currency rates up"""
        self.assertAlmostEqual(CAD.value_in(USD, date(2008, 4, 20)), 0.996115)
        self.assertAlmostEqual(CAD.value_in(EUR, date(2008, 4, 20)), 0.633141)
    
    def test_get_rate_with_pivotal(self):
        """It's possible to get a rate by using 2 records"""
        # if 1 CAD = 0.996115 USD and 1 CAD = 0.633141 then 0.996115 USD = 0.633141 then 1 USD = 0.633141 / 0.996115 EUR
        self.assertAlmostEqual(USD.value_in(EUR, date(2008, 4, 20)), 0.633141 / 0.996115)
    
    def test_get_rate_doesnt_exist(self):
        """Don't crash when trying to do pivotal calculation with non-existing currencies"""
        self.assertEqual(USD.value_in(PLN, date(2008, 4, 20)), 1 / 0.996115 / PLN.fallback_rate)


class DBWithPath(TestCase):
    def setUp(self):
        self.dbpath = Path(self.tmpdir()) + 'foo.db'
        db = RatesDB(self.dbpath)
        db.set_CAD_value(date(2008, 4, 20), 'USD', 1/0.996115)
    
    def test_get_rate_new_instance(self):
        """Use another instance to call get_rate on"""
        db = RatesDB(self.dbpath)
        self.assertAlmostEqual(db.get_rate(date(2008, 4, 20), 'CAD', 'USD'), 0.996115)
    

class DBWithConnection(TestCase):
    def setUp(self):
        self.con = sqlite.connect(':memory:')
        self.db = RatesDB(self.con)
    
    def test_tables(self):
        """the supplied connection is used instead"""
        try:
            self.con.execute("select * from rates where 1=2")
        except sqlite.OperationalError: # new db
            self.fail()
    

class CorruptPath(TestCase):
    def setUp(self):
        self.dbpath = self.tmppath() + 'foo.db'
        fh = io.open(self.dbpath, 'w')
        fh.write('corrupted')
        fh.close()
    
    def test_open_db(self):
        db = RatesDB(self.dbpath) # no crash. deletes the old file and start a new db
        db.set_CAD_value(date(2008, 4, 20), 'USD', 42)
        db = RatesDB(self.dbpath)
        self.assertEqual(db.get_rate(date(2008, 4, 20), 'USD', 'CAD'), 42)
    

class DBProblemAfterConnection(TestCase):
    def setUp(self):
        class MockConnection(sqlite.Connection): # can't mock sqlite3.Connection's attribute, so we subclass it
            mocking = False
            def execute(self, *args, **kwargs):
                if self.mocking:
                    raise sqlite.OperationalError()
                else:
                    return sqlite.Connection.execute(self, *args, **kwargs)
            
        
        con = MockConnection(':memory:')
        self.db = RatesDB(con)
        con.mocking = True
    
    def test_date_range(self):
        self.db.date_range('USD') # no crash
    
    def test_get_rate(self):
        self.db.get_rate(date(2008, 4, 20), 'USD', 'CAD') # no crash
    
    def test_set_rate(self):
        self.db.set_CAD_value(date(2008, 4, 20), 'USD', 42) # no crash
    
