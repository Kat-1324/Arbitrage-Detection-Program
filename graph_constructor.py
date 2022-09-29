"""
Brief: This script contains a class that builds a digraph matrix.
Description: The matrix represents a graph where nodes are currencies and weighted edges are the exchange rates.
             Exchange rates are calculated using the best bid and best ask in the order book.
"""

import numpy as np


class GraphConstructor:
    """ Constructs a digraph matrix. """

    def __init__(self, client, currencies):
        self.client = client  # Exchange client
        self.nodes = currencies  # Distinct currency codes [ccy0, ccy1, ..., ccyN]
        self.nodesKey = self._createCurrencyKeys()  # Record currency code to vertex number relation {ccy0: 0, ccy1: 1, ..., ccyN: N}
        self.edges = self._getCurrencyPairs()  # Record currency pairs [(BASE, QUOTE), (BASE, QUOTE), ..., (BASE, QUOTE)]

    def _createCurrencyKeys(self):
        """
        Records currency code to vertex number relation.

        RETURN
        ------
        - dictionary (dict): {ccy0: 0, ccy1: 1, ..., ccyN: N}
        """
        dictionary = {}
        for index, ccy in enumerate(self.nodes):
            dictionary[ccy] = index
        return dictionary

    def _getCurrencyPairs(self):
        """
        Finds all currency pairs given the currency codes.

         RETURN
         ------
         - graphEdges (list): [(BASE, QUOTE), (BASE, QUOTE), ..., (BASE, QUOTE)]
         """
        graphEdges = []

        for base in self.nodes:
            for quote in self.nodes:
                if self.client.checkCurrencyPairExistence(base, quote):
                    graphEdges.append((base, quote))

        return graphEdges

    def buildGraph(self):
        """
        Constructs matrix representing graph where currency codes are nodes and exchange rates are weighted edges.

        RETURN
         ------
        - graph (np.array): a (N+1, N+1) matrix
        - orderBooks (dict): { (BASE, QUOTE): { order book information }, ..., (BASE, QUOTE): { order book information } }
        """

        n = len(self.nodes)  # Number of nodes in graph
        orderBooks = {}  # Create store for order books
        graph = np.zeros((n, n))  # Create matrix to represent the digraph

        # Get all relevant order books
        for pair in self.edges:

            # pair[0] is base/volume currency code, pair[1] is quote/price currency code
            orderBooks[pair] = self.client.getOrderBook(pair[0], pair[1])

        # Processing is done separately from retrieval of order books so that they are retrieved almost simultaneously
        for pair in self.edges:

            # Get vertex number that each currency code corresponds to
            baseNode = self.nodesKey[pair[0]]
            quoteNode = self.nodesKey[pair[1]]

            # Calculate exchange rate for BASE --> QUOTE; this is equal to the best BID price
            bestBid = orderBooks[pair]['bids'][0][0]  # Get best bid (str)
            graph[baseNode, quoteNode] = -1 * np.log(eval(bestBid))  # Linearize and assign weight to edge

            # Calculate exchange rate for QUOTE --> BASE; this is equal to 1/(best ASK price)
            bestAsk = orderBooks[pair]['asks'][0][0]  # Get best ask (str)
            graph[quoteNode, baseNode] = -1 * np.log(1 / eval(bestAsk))  # Linearize and assign weight to edge

        return graph, orderBooks
