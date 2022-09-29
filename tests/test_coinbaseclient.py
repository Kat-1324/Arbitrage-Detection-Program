"""
Brief: Unit tests for coinbase_client.py
"""

from unittest import TestCase
from clients.coinbase.coinbase_client import CoinbaseClient, CurrencyNotFound


class TestCoinbaseClient(TestCase):
    """ Unit tests for CoinbaseClient class. """

    def setUp(self):
        self.client = CoinbaseClient()

    def test_getOrderBook(self):
        orderBookOne = self.client.getOrderBook("BTC", "USD")
        orderBookTwo = self.client.getOrderBook("BAT", "BTC")

        self.assertTrue("asks" in orderBookOne.keys())
        self.assertTrue("asks" in orderBookTwo.keys())

        self.assertTrue("bids" in orderBookOne.keys())
        self.assertTrue("bids" in orderBookTwo.keys())

    def test_getNotionalMinLimit(self):
        self.assertEqual(self.client.getNotionalMinLimit("BNT", "GBP"), '0.72')
        self.assertEqual(self.client.getNotionalMinLimit("CHZ", "USD"), '1')
        self.assertEqual(self.client.getNotionalMinLimit("ETH", "DAI"), '1')
        self.assertEqual(self.client.getNotionalMinLimit("GRT", "EUR"), '0.84')

    def test_getFees(self):
        self.assertEqual(self.client.getFees(50), '0.0060')
        self.assertEqual(self.client.getFees(5500000), '0.0018')

    def test_getBasePrecision(self):
        self.assertEqual(self.client.getBasePrecision('KRL', 'EUR'), -1)
        self.assertEqual(self.client.getBasePrecision('LOKA', 'USD'), -2)
        self.assertEqual(self.client.getBasePrecision('LRC', 'BTC'), 0)

    def test_checkCurrenciesExistence(self):
        with self.assertRaises(CurrencyNotFound):
            self.client.checkCurrenciesExistence(['BTC', 'LEOPARD', 'ETH', 'UNICORN'])

        error = False
        try:
            self.client.checkCurrenciesExistence(['ACH', 'FORT', 'USDT'])
        except CurrencyNotFound:
            error = True
        self.assertFalse(error)

    def test_checkCurrencyPairExistence(self):
        self.assertTrue(self.client.checkCurrencyPairExistence('SUKU', 'USD'))
        self.assertTrue(self.client.checkCurrencyPairExistence('TRU', 'BTC'))

        self.assertFalse(self.client.checkCurrencyPairExistence('PENCIL', 'USD'))
        self.assertFalse(self.client.checkCurrencyPairExistence('FOX', 'FOX'))

    def tearDown(self):
        self.client.closeSession()