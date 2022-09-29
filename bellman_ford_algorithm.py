"""
Brief: This script contains a class that detects negative cycles in weighted digraphs using the Bellman-Ford algorithm.
Description: The Bellman-Ford algorithm computes the shortest path from a single source vertex to all the other vertices in a weighted digraph.
             It can handle negative and positive edge weights. It can determine if a digraph contains a negative cycle.
             We ASSUME that the digraph is a strongly connected component.
             Alternatively, there exists a Bellman-Ford algorithm implementation in the scipy.sparse.csgraph library;
             however it raises an error if a negative cycle is found and hence is not applicable for negative cycle retrieval.
"""

import numpy as np


class BellmanFordAlgorithm:
    """ Utilises the Bellman-Ford algorithm to detect existence of a negative cycle in a strongly connected weighted digraph. """

    def __init__(self, matrix):
        self.matrix = matrix
        self.vertices = matrix.shape[0]  # Number of vertices in the graph (int)
        self.distances = np.full(self.vertices, np.inf)  # Initialize distance to all vertices from source vertex to infinity (np.array)
        self.predecessors = np.full(self.vertices, -1)  # Initialize predecessor vertices store (np.array)
        self.negativeCycle = []  # Default empty list for containment of negative cycle if exists

    def initializeSourceVertex(self):
        """
        Picks the source vertex. As graph is strongly connected, any vertex can be a source vertex. We pick the source vertex to be vertex 0.
        """

        # Distance from source vertex to itself is zero
        self.distances[0] = 0

    def implementBellmanFordAlgorithm(self):
        """
        Apply Bellman-Ford algorithm to graph for |vertices|-1 iterations.
        """

        self.initializeSourceVertex()

        for _ in range(self.vertices - 1):

            frozenDistances = self.distances.copy()

            # Iterate over each row in the input matrix
            for yValue, row in enumerate(self.matrix):

                # Iterate over each column in the selected row of the input matrix
                for xValue, column in enumerate(row):

                    # Update distances and predecessor vertices if shorter path is found
                    if column != 0 and frozenDistances[yValue] + column < frozenDistances[xValue]:
                        self.distances[xValue] = self.distances[yValue] + column
                        self.predecessors[xValue] = yValue

    def getANegativeCycle(self):
        """
        Finds negative cycle in graph if exists. The negative cycle is found by relaxing the edges for |vertices|th time
        and observing if the shortest path changes. If several negative cycles exist, one is randomly picked using the logic below.
        """

        self.implementBellmanFordAlgorithm()

        frozenDistances = self.distances.copy()

        # Iterate over each row in the input matrix
        for yValue, row in enumerate(self.matrix):

            # Iterate over each column in the selected row of the input matrix
            for xValue, column in enumerate(row):

                # Check if a shorter path exists from source vertex which signals the existence of a negative cycle
                if column != 0 and frozenDistances[yValue] + column < frozenDistances[xValue]:
                    self.distances[xValue] = self.distances[yValue] + column
                    self.predecessors[xValue] = yValue

        # If a shorter path is found for any vertex then the negative cycle is calculated
        if True in (self.distances != frozenDistances):
            self._findCycle(list(self.distances != frozenDistances).index(True))


    def _findCycle(self, endVertex):
        """
        Finds the vertices in the negative cycle in order given that it exists.

        PARAMETERS
        ----------
        - endVertex (int): a vertex for which a shorter path has been found on the |vertices|th iteration of the algorithm
        """

        vertex = endVertex
        predecessor = self.predecessors[vertex]
        self.negativeCycle.append(vertex)

        for _ in range(self.vertices):

            vertex, predecessor = predecessor, self.predecessors[predecessor]

            if vertex not in self.negativeCycle:
                self.negativeCycle.append(vertex)
            else:
                index = self.negativeCycle.index(vertex)  # Get index
                self.negativeCycle = self.negativeCycle[index:].copy()  # Truncate cycle
                self.negativeCycle.reverse()
                break
