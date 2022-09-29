"""
Brief: Unit tests for arbitrage_data_collector.py
"""

from unittest import TestCase
from clients.coinbase.coinbase_client import CoinbaseClient
from arbitrage_data_collector import ArbitrageDataCollector


class TestArbitrageDataCollector(TestCase):
    """ Unit tests for ArbitrageDataCollector class. """

    def setUp(self):
        self.testData = ArbitrageDataCollector(
            client=CoinbaseClient(),
            nodesKey={'ETH': 0, 'USD': 1, 'BTC': 2},
            cycle=[2, 1, 0],
            edges=[('ETH', 'USD'), ('ETH', 'BTC'), ('BTC', 'USD')],
            orderBooks={('ETH', 'BTC'): {'bids': [['0.08084', '1.1', 1]], 'asks': [['0.08086', '0.15499973', 1]]},
                        ('ETH', 'USD'): {'bids': [['1751.27', '0.24731766', 1]], 'asks': [['1751.54', '0.35199679', 2]]},
                        ('BTC', 'USD'): {'bids': [['21652.44', '0.00163887', 1]], 'asks': [['21652.45', '0.04432124', 3]]}},
            tradedVolume=20000001
        )

    def test_initializationOfParameters(self):
        self.assertSequenceEqual(self.testData.cycle, ['BTC', 'USD', 'ETH'])
        self.assertDictEqual(self.testData.nodesKeyReversed, {0: 'ETH', 1: 'USD', 2: 'BTC'})

    def test_extractArbitrageData(self):
        """ Test if the arbitrage data is correctly collected. """
        arbitrageData = self.testData.extractArbitrageData()

        firstPair = arbitrageData[0]
        secondPair = arbitrageData[1]
        thirdPair = arbitrageData[2]

        self.assertTupleEqual(firstPair['pair'], ('BTC', 'USD'))
        self.assertTupleEqual(secondPair['pair'], ('ETH', 'USD'))
        self.assertTupleEqual(thirdPair['pair'], ('ETH', 'BTC'))

        self.assertEqual(firstPair['position'], 'short')
        self.assertEqual(secondPair['position'], 'long')
        self.assertEqual(thirdPair['position'], 'short')

        self.assertEqual(firstPair['availableQuantity'], '0.00163887')
        self.assertEqual(secondPair['availableQuantity'], '0.35199679')
        self.assertEqual(thirdPair['availableQuantity'], '1.1')

        self.assertEqual(firstPair['price'], '21652.44')
        self.assertEqual(secondPair['price'], '1751.54')
        self.assertEqual(thirdPair['price'], '0.08084')

        self.assertEqual(firstPair['fee'], '0.0015')
        self.assertEqual(secondPair['fee'], '0.0015')
        self.assertEqual(thirdPair['fee'], '0.0015')

        self.assertEqual(firstPair['basePrecision'], -8)
        self.assertEqual(secondPair['basePrecision'], -8)
        self.assertEqual(thirdPair['basePrecision'], -8)

        self.assertEqual(firstPair['notionalMinimumLimit'], '1')
        self.assertEqual(secondPair['notionalMinimumLimit'], '1')
        self.assertEqual(thirdPair['notionalMinimumLimit'], '0.00001')

    def tearDown(self):
        self.testData.client.closeSession()
