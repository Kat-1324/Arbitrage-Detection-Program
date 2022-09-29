"""
Brief: This script contains a class that analyses an arbitrage opportunity.
Description: The class calculates the maximum order sizes possible taking into account all the information on the exchange.
             The maximum order sizes are also corrected to take into account base currency precision.
             A check on the notional value of each order is carried out to ensure it is valid.
             If arbitrage is profitable and valid, then the order sequence and profit can be printed to the console.
"""

import numpy as np


class Arbitrage:
    """ Analyses arbitrage opportunity. """

    def __init__(self, arbitrageData):
        self.arbitrage = arbitrageData  # A list of dictionaries

    def calculateMaximumOrderSize(self):
        """
        Calculates maximum order size taking into account the available quantities, prices and fees in the order book

        RETURN
        ------
        - sizes (np.array): maximum possible order sizes in arbitrage opportunity
        """

        sizes = np.zeros(len(self.arbitrage))  # Initialize store of maximum order sizes
        amountAfterTrade = np.inf  # Variable to keep track of funds at the end of a trade

        for index, order in enumerate(self.arbitrage):

            fee = eval(order['fee'])  # Get fee
            price = eval(order['price'])  # Get price
            size = eval(order['availableQuantity'])  # Get size

            # Case if position is short
            if order['position'] == 'short':

                if amountAfterTrade <= size:
                    sizes[index] = amountAfterTrade
                    amountAfterTrade = amountAfterTrade * price * (1 - fee)

                else:  # amountAfterTrade > size
                    # Must readjust all previous maximum order sizes
                    sizes *= (size / amountAfterTrade)

                    # Update size for this order
                    sizes[index] = size
                    amountAfterTrade = size * price * (1 - fee)

            else:  # trade['position'] == 'long'

                if amountAfterTrade <= size * price * (1 + fee):
                    sizes[index] = amountAfterTrade / (price * (1 + fee))
                    amountAfterTrade = sizes[index]

                else:  # amountAfterTrade > size * price * (1 + fee)
                    # Must readjust all previous maximum order sizes
                    sizes *= ((size * price * (1 + fee)) / amountAfterTrade)

                    # Update size for this order
                    sizes[index] = size
                    amountAfterTrade = sizes[index]

        return sizes

    def adjustOrderSizeForBaseTickSize(self, sizes):
        """
        Adjusts all maximum order sizes to take into account maximum base currency precision.

        PARAMETERS
        ----------
        - sizes (np.array): raw maximum order sizes (don't take into account base currency precision)

        RETURN
        ------
        - adjustedOrderSizes (list): maximum order sizes that have been adjusted to the base currency precision
        """

        adjustedOrderSizes = []  # Initialize data store for adjusted order sizes
        sizes = sizes.copy()  # So that we are not altering the original array (due to way Python stores numpy arrays)

        for index in range(len(sizes)):

            size = sizes[index]  # Get order size
            precision = self.arbitrage[index]['basePrecision']
            adjustedOrderSize = int(size * (10 ** -precision)) * (10 ** precision)

            if adjustedOrderSize != size:
                sizes *= (adjustedOrderSize / size)  # Readjust all the following order sizes
            adjustedOrderSizes.append(adjustedOrderSize)

        return adjustedOrderSizes

    def checkNotionalMinimumLimit(self, adjustedOrderSizes):
        """
        Checks if the notional value exceeds the notional minimum limit for all currency pairs.

        PARAMETERS
        ----------
        - adjustedOrderSizes (list): maximum order sizes that have been adjusted to the base currency precision

        RETURN
        ------
        - True or False (Boolean): True if all notional values pass the requirement else False
        """

        for index in range(len(adjustedOrderSizes)):

            notionalMinLimit = eval(self.arbitrage[index]['notionalMinimumLimit'])  # Get notional minimum limit
            notional = adjustedOrderSizes[index] * eval(self.arbitrage[index]['price'])

            if notional <= notionalMinLimit:
                return False

        return True

    def calculateProfit(self, adjustedSizes):
        """
        Calculates profit of the arbitrage.

        PARAMETERS
        ----------
        - adjustedOrderSizes (list): maximum order sizes that have been adjusted to the base currency precision

        RETURN
        ------
        - profit (float): profit at the end of the arbitrage set of trades
        """

        # Get initial amount
        if self.arbitrage[0]['position'] == 'short':
            startAmount = adjustedSizes[0]
        else:
            startAmount = adjustedSizes[0] * eval(self.arbitrage[0]['price']) * (1 - eval(self.arbitrage[0]['fee']))

        # Get final amount
        if self.arbitrage[-1]['position'] == 'long':
            endAmount = adjustedSizes[-1]
        else:
            endAmount = adjustedSizes[-1] * eval(self.arbitrage[-1]['price']) * (1 - eval(self.arbitrage[-1]['fee']))

        profit = endAmount - startAmount

        return profit

    def printOrderSequence(self, adjustedSizes):
        """
        Should only be called if a valid and profitable arbitrage is found. Prints order sequence and profit to the console.

        PARAMETERS
        ----------
        - adjustedOrderSizes (list): maximum order sizes that have been adjusted to the base currency precision
        """

        for index in range(len(self.arbitrage)):

            if self.arbitrage[index]['position'] == 'short':  # Deal with case if take a short position

                print('Order {orderNumber}: Sell {base}, to get {quote}, via an order of {size} {base} at price {price} {quote}.\n   --> Get {amount} {quote} having paid a fee of {fee} {quote}.'.format(
                    orderNumber=str(index+1),
                    base=self.arbitrage[index]['pair'][0],
                    quote=self.arbitrage[index]['pair'][1],
                    size=adjustedSizes[index],
                    price=self.arbitrage[index]['price'],
                    amount=adjustedSizes[index]*eval(self.arbitrage[index]['price'])*(1-eval(self.arbitrage[index]['fee'])),
                    fee=adjustedSizes[index]*eval(self.arbitrage[index]['price'])*eval(self.arbitrage[index]['fee'])
                ))

            else:  # Deal with case if take a long position

                print('Order {orderNumber}: Buy {base}, using {quote}, via an order of {size} {base} at price {price} {quote}.\n   --> Pay {amount} {quote} and a a fee of {fee} {quote}.'.format(
                    orderNumber=str(index+1),
                    base=self.arbitrage[index]['pair'][0],
                    quote=self.arbitrage[index]['pair'][1],
                    size=adjustedSizes[index],
                    price=self.arbitrage[index]['price'],
                    amount=adjustedSizes[index] * eval(self.arbitrage[index]['price']),
                    fee=adjustedSizes[index] * eval(self.arbitrage[index]['price']) * eval(self.arbitrage[index]['fee'])
                ))

        if self.arbitrage[0]['position'] == 'short':
            print("\nA profit of {profit} {ccy} can be made via arbitrage.".format(profit=self.calculateProfit(adjustedSizes), ccy=self.arbitrage[0]['pair'][0]))
        else:
            print("\nA profit of {profit} {ccy} can be made via arbitrage.".format(profit=self.calculateProfit(adjustedSizes), ccy=self.arbitrage[0]['pair'][1]))
