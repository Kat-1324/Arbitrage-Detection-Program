"""
Brief: Unit tests for arbitrage.py
"""

from unittest import TestCase
from arbitrage import Arbitrage


class TestArbitrage(TestCase):
    """ Unit tests for Arbitrage class. """

    def setUp(self):
        self.testDataOne = Arbitrage([
            {'pair': ('A', 'B'), 'position': 'short', 'availableQuantity': '10', 'price': '10', 'fee': '0.01',
             'basePrecision': -4, 'quotePrecision': None, 'notionalMinimumLimit': '0.01'},
            {'pair': ('B', 'C'), 'position': 'long', 'availableQuantity': '5', 'price': '10', 'fee': '0.01',
             'basePrecision': -2, 'quotePrecision': None, 'notionalMinimumLimit': '0.1'},
            {'pair': ('C', 'D'), 'position': 'short', 'availableQuantity': '1', 'price': '2', 'fee': '0.03',
             'basePrecision': 0, 'quotePrecision': None, 'notionalMinimumLimit': '0.55'},
            {'pair': ('D', 'E'), 'position': 'long', 'availableQuantity': '10', 'price': '3', 'fee': '0.01',
             'basePrecision': -5, 'quotePrecision': None, 'notionalMinimumLimit': '1'},
            {'pair': ('E', 'A'), 'position': 'short', 'availableQuantity': '100', 'price': '2', 'fee': '0.02',
             'basePrecision': -4, 'quotePrecision': None, 'notionalMinimumLimit': '1'}
        ])
        self.testDataTwo = Arbitrage([
                {'pair': ('A', 'B'), 'position': 'short', 'availableQuantity': '10', 'price': '10', 'fee': '0.01',
                 'basePrecision': -5, 'quotePrecision': None, 'notionalMinimumLimit': '1'},
                {'pair': ('B', 'C'), 'position': 'short', 'availableQuantity': '100', 'price': '2', 'fee': '0.02',
                 'basePrecision': -4, 'quotePrecision': None, 'notionalMinimumLimit': '0.1'},
                {'pair': ('C', 'D'), 'position': 'long', 'availableQuantity': '5', 'price': '10', 'fee': '0.01',
                 'basePrecision': -2, 'quotePrecision': None, 'notionalMinimumLimit': '0.01'},
                {'pair': ('D', 'E'), 'position': 'short', 'availableQuantity': '1', 'price': '2', 'fee': '0.03',
                 'basePrecision': -2, 'quotePrecision': None, 'notionalMinimumLimit': '1'},
                {'pair': ('E', 'A'), 'position': 'long', 'availableQuantity': '10', 'price': '3', 'fee': '0.01',
                 'basePrecision': -5, 'quotePrecision': None, 'notionalMinimumLimit': '0.72'}
        ])

    def test_calculateMaximumOrderSize(self):
        """ Test if the maximum order sizes are calculated correctly. """
        sizesOne = self.testDataOne.calculateMaximumOrderSize()
        sizesTwo = self.testDataTwo.calculateMaximumOrderSize()

        expectedSizesOne = [1.020202, 1.0, 1.0, 0.64026403, 0.64026403]
        expectedSizesTwo = [0.52051123, 5.15306122, 1.0, 1.0, 0.64026403]

        for i in range(5): self.assertAlmostEqual(sizesOne[i], expectedSizesOne[i])
        for i in range(5): self.assertAlmostEqual(sizesTwo[i], expectedSizesTwo[i])

    def test_adjustOrderSizeForBaseTickSize(self):
        """ Test if the maximum order sizes are adjusted correctly to account for the base currency precision. """
        sizesOne = self.testDataOne.calculateMaximumOrderSize()
        sizesTwo = self.testDataTwo.calculateMaximumOrderSize()

        adjustedSizesOne = self.testDataOne.adjustOrderSizeForBaseTickSize(sizesOne)
        adjustedSizesTwo = self.testDataTwo.adjustOrderSizeForBaseTickSize(sizesTwo)

        expectedAdjustedOrderSizeOne = [1.0202, 0.99, 0, 0, 0]
        expectedAdjustedOrderSizeTwo = [0.52051, 5.1530, 0.99, 0.99, 0.63386]

        for i in range(5): self.assertAlmostEqual(adjustedSizesOne[i], expectedAdjustedOrderSizeOne[i])
        for i in range(5): self.assertAlmostEqual(adjustedSizesTwo[i], expectedAdjustedOrderSizeTwo[i])

    def test_checkNotionalMinimumLimit(self):
        """ Test if the check for the notional minimum limit is done correctly. """
        sizesOne = self.testDataOne.calculateMaximumOrderSize()
        sizesTwo = self.testDataTwo.calculateMaximumOrderSize()

        adjustedSizesOne = self.testDataOne.adjustOrderSizeForBaseTickSize(sizesOne)
        adjustedSizesTwo = self.testDataTwo.adjustOrderSizeForBaseTickSize(sizesTwo)

        self.assertFalse(self.testDataOne.checkNotionalMinimumLimit(adjustedSizesOne))
        self.assertTrue(self.testDataTwo.checkNotionalMinimumLimit(adjustedSizesTwo))

    def test_calculateProfit(self):
        """ Test if the profit is calculated correctly. """
        sizesOne = self.testDataOne.calculateMaximumOrderSize()
        sizesTwo = self.testDataTwo.calculateMaximumOrderSize()

        adjustedSizesOne = self.testDataOne.adjustOrderSizeForBaseTickSize(sizesOne)
        adjustedSizesTwo = self.testDataTwo.adjustOrderSizeForBaseTickSize(sizesTwo)

        self.assertAlmostEqual(self.testDataOne.calculateProfit(adjustedSizesOne), -1.0202)
        self.assertAlmostEqual(self.testDataTwo.calculateProfit(adjustedSizesTwo), 0.11335)
