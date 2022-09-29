"""
Brief: This script contains a class that collects the information required to analyse the arbitrage opportunity.
Description: For each trade that needs to be placed information such as price, position and base/quote precision is collected for each currency pair.
"""

class ArbitrageDataCollector:
    """ Collects data required to analyse arbitrage. """

    def __init__(self, client, nodesKey, cycle, edges, orderBooks, tradedVolume):
        self.client = client  # Exchange client
        self.nodesKeyReversed = dict([(value, key) for key, value in nodesKey.items()])  # Currency code to vertex number relation {0: ccy0, 1: ccy1, ..., N: ccyN}
        self.cycle = [self.nodesKeyReversed[i] for i in cycle]  # Currency codes in arbitrage cycle in order
        self.edges = edges  # List of edges [(BASE, QUOTE), (BASE, QUOTE), ..., (BASE, QUOTE)]
        self.orderBooks = orderBooks  # Dictionary { (BASE, QUOTE) : order book, ..., (BASE, QUOTE) : order book }
        self.tradedVolume = tradedVolume  # 30-day trading volume in USD

    def extractArbitrageData(self):
        """
        Extract information w.r.t. each currency pair in arbitrage cycle.

        RETURN
        ------
        - arbitrageData (list): information stored in dictionaries in order of appearance in arbitrage cycle
            Each dictionary has:
            - 'pair' (str | key) --> (BASE, QUOTE) (tuple of currency codes)
            - 'position' (str | key) --> 'short' or 'long' (str)
            - 'availableQuantity' (str | key) --> quantity of base currency available at best bid/ask price in order book (str)
            - 'price' (str | key) --> best bid/ask price in order book (str)
            - 'fee' (str | key) --> fee charged per trade (decimal representation of the percentage)
            - 'basePrecision' (str | key) --> base currency precision (int)
            - 'notionalMinimumLimit' (str | key) --> notional minimum limit (str)
        """

        n = len(self.cycle)  # Get number of nodes in cycle
        arbitrageData = []  # Initialize data store

        # Iterate through arbitrage cycle
        for index, currency in enumerate(self.cycle):

            if (currency, self.cycle[(index + 1) % n]) in self.edges:

                base = currency  # Get base currency
                quote = self.cycle[(index + 1) % n]  # Get quote currency

                arbitrageData.append(dict([
                    ('pair', (base, quote)),
                    ('position', 'short'),
                    ('availableQuantity', self.orderBooks[(base, quote)]['bids'][0][1]),
                    ('price', self.orderBooks[(base, quote)]['bids'][0][0]),
                    ('fee', self.client.getFees(self.tradedVolume)),
                    ('basePrecision', self.client.getBasePrecision(base, quote)),
                    ('notionalMinimumLimit', self.client.getNotionalMinLimit(base, quote))
                ]))

            else:

                base = self.cycle[(index + 1) % n]  # Get base currency
                quote = currency  # Get quote currency

                arbitrageData.append(dict([
                    ('pair', (base, quote)),
                    ('position', 'long'),
                    ('availableQuantity', self.orderBooks[(base, quote)]['asks'][0][1]),
                    ('price', self.orderBooks[(base, quote)]['asks'][0][0]),
                    ('fee', self.client.getFees(self.tradedVolume)),
                    ('basePrecision', self.client.getBasePrecision(base, quote)),
                    ('notionalMinimumLimit', self.client.getNotionalMinLimit(base, quote))
                ]))

        return arbitrageData
