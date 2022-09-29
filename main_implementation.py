"""
Brief: This script contains the main function linking all of the components in the arbitrage detection project.
"""

from graph_constructor import GraphConstructor
from strongly_connected_components import ConnectedComponents
from bellman_ford_algorithm import BellmanFordAlgorithm
from arbitrage_data_collector import ArbitrageDataCollector
from arbitrage import Arbitrage


def main(client, currencies, tradedVolume=1000000000000):
    """
     PARAMETERS
     ----------
     - client (object): exchange client object
     - currencies (list): distinct currency codes
     - tradedVolume (int/float): 30-day USD trading volume required for fee calculation
     """

    # Check if all input currencies are available on the exchange; raises an error if not
    client.checkCurrenciesExistence(currencies)

    graphObject = GraphConstructor(client, currencies)
    graph, orderBooks = graphObject.buildGraph()

    # Get information regarding the strongly connected components in the graph
    connectedComponentsObject = ConnectedComponents(graph)
    connectedComponents = connectedComponentsObject.getConnectedComponents()

    # Check if there are any strongly connected components with 3 or more vertices
    if len(connectedComponents['components']) != 0:

        arbTemp = False  # Keep track if arbitrage has been detected or not

        # Iterate through the connected components
        for index, component in enumerate(connectedComponents['components']):

            BFObject = BellmanFordAlgorithm(component['subGraph'])
            BFObject.getANegativeCycle()
            negativeCycle = BFObject.negativeCycle  # Get negative cycle

            if len(negativeCycle) != 0:

                arbTemp = True  # Arbitrage has been found so set to True

                # Decode the cycle
                vertexDict = dict(component['componentVerticesMap'])
                arbitrageCycle = [vertexDict[v] for v in negativeCycle]  # Arbitrage cycle with original vertex numbers

                arbDataObject = ArbitrageDataCollector(
                    client=client,
                    nodesKey=graphObject.nodesKey,
                    cycle=arbitrageCycle,
                    edges=graphObject.edges,
                    orderBooks=orderBooks,
                    tradedVolume=tradedVolume
                )
                arbData = arbDataObject.extractArbitrageData()
                arbitrage = Arbitrage(arbData)

                sizes = arbitrage.calculateMaximumOrderSize()
                adjustedSizes = arbitrage.adjustOrderSizeForBaseTickSize(sizes)  # Adjust maximum order size for base currency precision

                # Check notional minimum limit requirement is passed
                if arbitrage.checkNotionalMinimumLimit(adjustedSizes):  # If True

                    # Calculate profit
                    if arbitrage.calculateProfit(adjustedSizes) > 0:
                        print("A profitable arbitrage has been found.\n")
                        arbitrage.printOrderSequence(adjustedSizes)  # Prints order sequence and profit to console
                    else:
                        print('An arbitrage has been found. It satisfies the notional minimum limit requirements. It makes NO profit.')
                else:
                    print('An arbitrage has been found. It does NOT satisfy the notional minimum limit requirements.')

                break

            if not arbTemp:
                print('No arbitrage has been found.')

    else:
        print('Given the currencies and the client, it is not possible to get an arbitrage.')

    client.closeSession()
