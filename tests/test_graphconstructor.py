"""
Brief: Unit tests for graph_constructor.py
"""

from unittest import TestCase
from clients.coinbase.coinbase_client import CoinbaseClient
from graph_constructor import GraphConstructor

import numpy as np


class TestGraphConstructor(TestCase):
    """ Unit tests for GraphConstructor class """

    def setUp(self):
        self.testGraph = GraphConstructor(CoinbaseClient(), ['BTC', 'BOBA', 'ETH', 'USDT'])

    def test_initializationOfParameters(self):
        """ Test if the attributes are correctly initialized """
        self.assertIsInstance(self.testGraph.client, CoinbaseClient)
        self.assertSequenceEqual(self.testGraph.nodes, ['BTC', 'BOBA', 'ETH', 'USDT'])
        self.assertDictEqual(self.testGraph.nodesKey, {'BOBA': 1, 'BTC': 0, 'USDT': 3, 'ETH': 2})
        self.assertEqual(len(self.testGraph.edges), 4)
        self.assertSetEqual(set(self.testGraph.edges), {('BOBA', 'USDT'), ('ETH', 'BTC'), ('ETH', 'USDT'), ('BTC', 'USDT')})

    def test_buildGraph(self):
        """ Test if the matrix representation of the graph is constructed correctly """
        graph, orderBooks = self.testGraph.buildGraph()
        for i, j in [(0, 0), (1, 1), (2, 2), (3, 3), (1, 0), (0, 1), (1, 2), (2, 1)]:
            self.assertEqual(graph[i, j], 0)

        self.assertAlmostEqual(np.exp(-graph[1, 3]), eval(orderBooks[('BOBA', 'USDT')]['bids'][0][0]))
        self.assertAlmostEqual(np.exp(-graph[2, 0]), eval(orderBooks[('ETH', 'BTC')]['bids'][0][0]))

        self.assertAlmostEqual(np.exp(-graph[3, 1]), 1/eval(orderBooks[('BOBA', 'USDT')]['asks'][0][0]))
        self.assertAlmostEqual(np.exp(-graph[0, 2]), 1/eval(orderBooks[('ETH', 'BTC')]['asks'][0][0]))

    def tearDown(self):
        self.testGraph.client.closeSession()
