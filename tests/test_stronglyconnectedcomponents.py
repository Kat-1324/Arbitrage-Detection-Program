"""
Brief: Unit tests for strongly_connected_components.py
"""

from unittest import TestCase
from strongly_connected_components import ConnectedComponents

import numpy as np


class TestConnectedComponents(TestCase):
    """ Unit tests for the ConnectedComponents class. """

    def setUp(self):
        self.graphOne = ConnectedComponents([[0, 0, 2],
                                             [0, 0, 0],
                                             [-1, 0, 0]])
        self.graphTwo = ConnectedComponents([[0, 1, 0, 0, 9, 0, 0],
                                             [0, 0, 0, 0, 0, 0, 0],
                                             [0, 0, 0, -4, 0, 0, 0],
                                             [0, 0, 0, 0, 1, 0, 0],
                                             [0, 0, -3, 0, 0, 0, 0],
                                             [0, 1, 0, 0, 2, 0, -1],
                                             [0, 0, 0, 0, 0, 1, 0]])

    def test_attributeInitialization(self):
        """ Test if the correct number of components and labels are instantiated. """
        self.assertEqual(self.graphOne.numberOfComponents, 2)
        self.assertEqual(self.graphTwo.numberOfComponents, 4)

        self.assertSequenceEqual(list(self.graphOne.componentLabels), [0, 1, 0])
        self.assertSequenceEqual(list(self.graphTwo.componentLabels), [2, 1, 0, 0, 0, 3, 3])

    def test_getConnectedComponents(self):
        """ Test if the graph is correctly processed. """
        componentsOne = self.graphOne.getConnectedComponents()
        componentsTwo = self.graphTwo.getConnectedComponents()

        self.assertSequenceEqual(componentsOne['components'], [])
        self.assertSequenceEqual(sorted(componentsTwo['components'][0]['componentVertices']), [2, 3, 4])
        self.assertSetEqual(set(componentsTwo['components'][0]['componentVerticesMap']), {(0, 2), (1, 3), (2, 4)})
        for row in componentsTwo['components'][0]['subGraph'] - np.array([[0, -4, 0], [0, 0, 1], [-3, 0, 0]]):
            for entry in row:
                self.assertEqual(entry, 0)

        self.assertSequenceEqual(sorted(componentsOne['isolatedVertices']), [0, 1, 2])
        self.assertSequenceEqual(sorted(componentsTwo['isolatedVertices']), [0, 1, 5, 6])
