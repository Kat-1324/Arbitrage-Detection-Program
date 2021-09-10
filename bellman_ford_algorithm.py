import numpy as np

def find_cycle(predecessors):
    """Given an array containing the predecessors of each vertex after the final iteration of the Bellman-Ford Algorithm, finds the negative cycle, given that it exists.

    INPUTS
    - predecessors: a ndarray (n,) containing the predecessors of each vertex after the final iteration of the Bellman-Ford Algorithm

    OUPUTS 
    - cycle: a list containing the vertices of the negative cycle in order"""

    # Iterate over the input ndarray, one vertex at a time, to identify the negative cycle
    for index, pred_value in enumerate(predecessors):

        # Check if the current vertex is reachable from the source vertex
        if pred_value is None:
            continue

        # Initiate a variable to store the vertices of the negative cycle
        cycle = []

        # If current vertex is reachable from the source, append it to the list as the starting vertex of the cycle
        cycle.append(index)

        # Follow the predecessors until the negative cycle is found, or the path terminates
        # At most n iterations are needed, as there are n vertices in the graph
        for _ in range(predecessors.shape[0]):
            
            # Update the index and pred_value variable values
            index, pred_value = pred_value, predecessors[pred_value]

            # Check if the path terminates before forming a cycle
            if index is None:
                break

            # Check if the negative cycle has been found, i.e.: check if the current vertex has already been previously appended to the cycle
            if index in cycle:
                cycle = cycle[cycle.index(index):]  # Retrieve the negative cycle from the current list of vertices
                cycle.reverse()
                return cycle

            cycle.append(index)  # Add the current vertex to the cycle list    

def bellman_ford(matrix):
    """Given a directed graph, uses the Bellman-Ford Algorithm to determine if a negative cycle exists. 

    INPUTS 
    - matrix: a (n,n) matrix containing the weights of the edges of the directed graph

    OUTPUTS 
    - cycle: a list containing the vertices of the negative cycle in order, if exists; otherwise outputs an empty list"""

    # Retrieve the number of vertices in the graph
    vertices = matrix.shape[0]  # The value is n

    # Initialize counter to keep track of the vertices that have been visited after each Bellman-Ford Algorithm application
    counter = [False] * vertices

    # Initialize a variable to store True if a negative cycle exists; False if it doesn't
    present = False

    while False in counter:
        
        # Initialize variables to store the shortest distance and predecessor vertices
        distance = np.full(vertices, np.inf)  # A ndarray (n,) filled with inf
        predecessor = np.full(vertices, None)  # A ndarray (n,) filled with None

        # Find the False with the smallest index in counter to locate the current source vertex
        unreached_node = counter.index(False)
        distance[unreached_node] = 0  # Set current source vertex distance to zero

        # Implement the Bellman-Ford Algorithm to determine if a negative cycle exists with current vertex as source
        for iteration in range(vertices - 1):

            # Iterate over each row in the input matrix
            for y_value, row in enumerate(matrix):

                # Iterate over each column in the selected row of the input matrix
                for x_value, column in enumerate(row):

                    # Update the distances and predecessor values if a shorter path is found
                    if distance[y_value] + column < distance[x_value] and column != 0:
                        distance[x_value] = distance[y_value] + column
                        predecessor[x_value] = y_value

        # Check if there is a negative cycle present with the current source vertex
        # Iterate over each row in the input matrix
        for y_value, row in enumerate(matrix):

            # Iterate over each column in the selected row of the input matrix
            for x_value, column in enumerate(row):

                if distance[y_value] + column < distance[x_value] and column != 0:
                    distance[x_value] = distance[y_value] + column
                    predecessor[x_value] = y_value
                    present = True  # Set true as a negative cycle has been detected

        # Call the find_cycle function defined above to find the existing negative cycle
        if present is True:
            cycle = find_cycle(predecessor)
            return cycle

        # Update the counter list to note all the vertices visited in this Bellman-Ford Algorithm implementation
        for i in range(vertices):
            if counter[i] == False and distance[i] != np.inf:
                counter[i] = True

    return []
