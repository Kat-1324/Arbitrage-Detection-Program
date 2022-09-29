"""
Brief: This script contains a class that finds and analyses strongly connected components in a given weighted digraph.
Description: A graph is said to be strongly connected if every vertex is reachable from every other vertex.
             Strongly connected components partition a graph into sub-graphs that themselves are strongly connected.
             A cycle can only exist in a strongly connected component.
"""

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


class ConnectedComponents:
    """ Finds strongly connected components in a weighted digraph. """

    def __init__(self, matrix):
        self.matrix = csr_matrix(matrix)  # Sparse matrix
        self.numberOfComponents, self.componentLabels = self._getDetails()

    def _getDetails(self):
        """
        Finds all strongly connected components using scipy.sparse.csgraph library in the graph.

        RETURN
        ------
        - n_components (int): number of strongly connected components
        - labels (list): indicates which vertices belong to the same component
        """
        n_components, labels = connected_components(csgraph=self.matrix,
                                                    directed=True,
                                                    connection='strong',
                                                    return_labels=True)
        return n_components, list(labels)

    def getConnectedComponents(self):
        """
        Collates information about strongly connected components.

        RETURN
        ------
        - vertexInformation (dict):
            - 'isolatedVertices' (str | key) --> all vertices from connected components with 1 or 2 vertices (list | value)
            - 'components' (str | key) --> information about connected components with 3 or more vertices (list of dictionaries | value)
                - 'subGraph' (str | key) --> sub-matrix of original matrix containing the connected component only (np.array | value)
                - 'componentVertices' (str | key) --> vertices in connected component (list | value)
                - 'componentVerticesMap' (str | key) --> list of tuples mapping new sub-graph vertex to original digraph vertex (list | value)
        """
        vertexInformation = {'components': [], 'isolatedVertices': []}  # Initialize data store

        # Iterate through all of the connected components
        for component in range(self.numberOfComponents):

            verticesInComponent = self.componentLabels.count(component)  # Get number of vertices in connected component

            if verticesInComponent <= 2:  # Discard any connected components with 1 or 2 vertices
                for index, vertex in enumerate(self.componentLabels):
                    if vertex == component:
                        vertexInformation['isolatedVertices'].append(index)
            else:
                # TODO - ensure all vertices have more than 2 degrees in the connected component (not essential though)
                componentVertices = []
                for index, vertex in enumerate(self.componentLabels):
                    if vertex == component:
                        componentVertices.append(index)  # Keep track of vertices in connected component

                vertexInformation['components'].append({
                                                        'subGraph': self.matrix[componentVertices, :][:, componentVertices].toarray(),
                                                        'componentVertices': componentVertices,
                                                        'componentVerticesMap': [(i, v) for i, v in enumerate(componentVertices)]
                                                        })

        return vertexInformation
