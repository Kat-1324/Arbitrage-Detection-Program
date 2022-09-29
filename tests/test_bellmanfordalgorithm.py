"""
Brief: Unit tests for bellman_ford_algorithm.py
"""

from unittest import TestCase
from bellman_ford_algorithm import BellmanFordAlgorithm

import numpy as np


class TestBellmanFordAlgorithm(TestCase):
    """ Unit tests for the BellmanFordAlgorithm class. """

    def setUp(self):
        """ Contains negative cycle - self.testMatrixOne
        Contains no negative cycle - self.testMatrixTwo
        Contains negative cycle - self.testMatrixThree """
        self.testMatrixOne = BellmanFordAlgorithm(np.array([[0,  2,  0,  0],
                                                            [1,  0, -1,  0],
                                                            [0,  0,  0, -1],
                                                            [1, -1,  0,  0]]))
        self.testMatrixTwo = BellmanFordAlgorithm(np.array([[0, 3, 1, 1, 0, 4],
                                                            [0, 0, 2, 7, 1, 0],
                                                            [-1, -1, 0, 0, 0, 1],
                                                            [1, 0, 2, 0, 0, 6],
                                                            [9, 1, 0, 1, 0, 0],
                                                            [0, 1, 3, 0, -1, 0]]))
        self.testMatrixThree = BellmanFordAlgorithm(np.array([[0, 1, 0, 0, 1, 0],
                                                            [0, 0, 1, 0, 0, 0],
                                                            [0, 1, 0, 1, -1, 3],
                                                            [0, 0, 0, 0, 0, 2],
                                                            [0, 0, -1, 0, 0, 0],
                                                            [-1, 0, 0, 0, 0, 0]]))

    def test_instantiationOfParameters(self):
        """ Test if object is correctly instantiated """
        self.assertEqual(self.testMatrixOne.vertices, 4)
        self.assertEqual(self.testMatrixTwo.vertices, 6)

        self.assertEqual(self.testMatrixOne.distances.shape[0], 4)
        self.assertEqual(self.testMatrixTwo.distances.shape[0], 6)
        self.assertTrue(False not in (self.testMatrixOne.distances == np.array([np.inf, np.inf, np.inf, np.inf])))
        self.assertTrue(False not in (self.testMatrixTwo.distances == np.array([np.inf, np.inf, np.inf, np.inf, np.inf, np.inf])))

        self.assertEqual(self.testMatrixOne.predecessors.shape[0], 4)
        self.assertEqual(self.testMatrixTwo.predecessors.shape[0], 6)
        self.assertTrue(False not in (self.testMatrixOne.predecessors == np.array([-1, -1, -1, -1])))
        self.assertTrue(False not in (self.testMatrixTwo.predecessors == np.array([-1, -1, -1, -1, -1, -1])))

    def test_initializeSourceVertex(self):
        """ Test if the correct distance is set from source vertex to itself """
        self.testMatrixOne.initializeSourceVertex()
        self.testMatrixTwo.initializeSourceVertex()

        self.assertEqual(self.testMatrixOne.distances[0], 0)
        self.assertEqual(self.testMatrixTwo.distances[0], 0)
        for index in range(1, 4):
            self.assertEqual(self.testMatrixOne.distances[index], np.inf)
        for index in range(1, 6):
            self.assertEqual(self.testMatrixTwo.distances[index], np.inf)

    def test_implementBellmanFordAlgorithm(self):
        """ Test if the Bellman-Ford algorithm correctly calculates distances and predecessor vertices,
        given that it goes through |vertices|-1 iterations """

        self.testMatrixOne.implementBellmanFordAlgorithm()
        self.testMatrixTwo.implementBellmanFordAlgorithm()
        self.testMatrixThree.implementBellmanFordAlgorithm()

        for index, distance in enumerate([0, 2, 1, 0]):
            self.assertEqual(self.testMatrixOne.distances[index], distance)
        for index, distance in enumerate([0, 0, 1, 1, 1, 2]):
            self.assertEqual(self.testMatrixTwo.distances[index], distance)
        for index, distance in enumerate([0, -1, -2, -1, -3, 1]):
            self.assertEqual(self.testMatrixThree.distances[index], distance)

        for index, predecessorVertex in enumerate([-1, 0, 1, 2]):
            self.assertEqual(self.testMatrixOne.predecessors[index], predecessorVertex)
        for index, predecessorVertex in enumerate([-1, 2, 0, 0, 5, 2]):
            self.assertEqual(self.testMatrixTwo.predecessors[index], predecessorVertex)
        for index, predecessorVertex in enumerate([-1, 2, 4, 2, 2, 2]):
            self.assertEqual(self.testMatrixThree.predecessors[index], predecessorVertex)

    def test_getNegativeCycle(self):
        """ Test if a negative cycle is correctly detected or not """
        self.testMatrixOne.getANegativeCycle()
        self.testMatrixTwo.getANegativeCycle()
        self.testMatrixThree.getANegativeCycle()

        self.assertListEqual(self.testMatrixOne.negativeCycle, [2, 3, 1])
        self.assertListEqual(self.testMatrixTwo.negativeCycle, [])
        self.assertListEqual(self.testMatrixThree.negativeCycle, [4, 2])

    def test_findCycle(self):
        """ Test if a cycle is correctly identified """
        additionalTestMatrix = BellmanFordAlgorithm(np.array([1]))

        self.testMatrixOne.predecessors = [-1, 3, 1, 2]
        additionalTestMatrix.predecessors = [3, 3, 4, 2, 0, 2]
        additionalTestMatrix.vertices = 6

        self.testMatrixOne._findCycle(1)
        additionalTestMatrix._findCycle(4)

        self.assertListEqual(self.testMatrixOne.negativeCycle, [2, 3, 1])
        self.assertListEqual(additionalTestMatrix.negativeCycle, [2, 3, 0, 4])
