from coinbase.coinbaseClient import CoinbaseClient
from bellman_ford_algorithm import bellman_ford

import numpy as np

# Create a Coinbase Pro client object
coinbase = CoinbaseClient()


def coinbase_currencies():
    """Retrieves a list of names of the existing currencies in use on Coinbase Pro. Not all currencies may be currently in use for trading.

    OUTPUTS
    - potential_nodes: a list containing names of all the existing currencies in use on Coinbase Pro"""

    # Get the list containing information about each currency on Coinbase Pro
    available_currencies = coinbase.get_currencies()
    
    # Create a list containing names of the existing currencies on Coinbase Pro
    potential_nodes = [currency['id'] for currency in available_currencies]

    return potential_nodes


def coinbase_currency_pairs():
    """Retrieves a list of the names of the available currency pairs used for trading on Coinbase Pro.

    OUTPUTS
    - potential_edges: a list containing all of the existing currency pairs on Coinbase Pro"""

    # Get the list containing information about each currency pair used for trading on Coinbase Pro
    available_currency_pairs = coinbase.get_pairs()
    
    # Create a list containing the names of the existing currency pairs on Coinbase Pro; each pair has the format BASE-QUOTE (for example ETH-GBP)
    potential_edges = [currency_pair['id'] for currency_pair in available_currency_pairs]

    return potential_edges


def coinbase_process_nodes_and_edges(currencies):
    """Given a list of currencies, extracts the relevant currencies and currency pairs that exist on Coinbase Pro.

    INPUTS
    - currencies: a list containing the preferred currencies to be used in arbitrage detection

    OUTPUTS
    - nodes: a list containing the relevant currencies that exist on Coinbase Pro
    - edges: a list containing the relevant currency pairs that exist on Coinbase Pro"""

    # Create empty lists to store the currencies and their corresponding pairs
    nodes = []
    edges = []

    # Iterate through all of the existing currency pairs on Coinbase Pro
    for currency_pair in coinbase_currency_pairs():

        # Extract the base and quote currency from each pair; each currency pair has format BASE-QUOTE
        temp = currency_pair.index('-')  # All base-quote pairs are separated by '-'
        base = currency_pair[:temp]  # Base currency
        quote = currency_pair[temp+1:]  # Quote currency

        if (base in currencies) and (quote in currencies):
            edges.append(currency_pair)  # Add currency pair to the edges list
            if base not in nodes:
                nodes.append(base)  # Add base currency to nodes, if it has not been already added
            if quote not in nodes:
                nodes.append(quote)  # Add quote currency to nodes, if it has not been already added

    return nodes, edges


def coinbase_graph(nodes, edges):
    """Creates a matrix representing the directed graph where the currencies are the nodes, and the currency pairs
    are the edges. The weights of the edges are the exchange rates extracted from the Coinbase Pro exchange.

    INPUTS
    - nodes: a list containing the currencies, of length n
    - edges: a list containing the corresponding currency pairs

    OUTPUTS
    - graph: a ndarray (n,n) representing the directed graph
    - order_book: a dictionary containing the current order size and price available for each currency pair, with currency pairs as keys"""

    # Calculate how many vertices the graph will have; this corresponds to the number of currencies
    n = len(nodes)

    # Create a matrix to store the directed graph
    graph = np.zeros((n, n))

    # Create a dictionary to store the current order sizes and corresponding prices for each currency pair
    order_book = dict((edge, {}) for edge in edges)

    # Create the directed graph
    for currency_pair in edges:
        
        # Extract the base and quote currency of the current currency pair
        temp = currency_pair.index('-')  # As all base-quote pairs are separated by '-'
        base = currency_pair[:temp]  # Base currency
        quote = currency_pair[temp + 1:]  # Quote currency

        # Locate the node each currency represents; these correspond to their index values in the list nodes
        base_index = nodes.index(base)
        quote_index = nodes.index(quote)

        # Retrieve the order book of the current currency pair
        order_book_temp = coinbase.get_order_book(currency_pair)

        # Calculate the exchange rate for BASE --> QUOTE; this is equal to the best BID price
        best_bid = order_book_temp['bids'][0][0]  # Returns a string containing the best bid
        order_book[currency_pair]['b_size'] = order_book_temp['bids'][0][1]  # Store the best bid size in the order_book
        order_book[currency_pair]['b_price'] = best_bid  # Store the best bid price in the order_book
        graph[base_index, quote_index] = -1 * np.log(eval(best_bid))  # Linearize and assign weight to the relevant edge

        # Calculate the exchange rate for QUOTE --> BASE; this is equal to 1/(best ASK price)
        best_ask = order_book_temp['asks'][0][0]  # Returns a string containing the best ask
        order_book[currency_pair]['a_size'] = order_book_temp['asks'][0][1]  # Store the best ask size in the order_book
        order_book[currency_pair]['a_price'] = best_ask  # Store the best ask price in the order_book
        graph[quote_index, base_index] = -1 * np.log(1 / eval(best_ask))  # Linearize and assign weight to the relevant edge

    return graph, order_book


def coinbase_arbitrage(currencies):
    """Given a list of currencies, outputs a currencies cycle if an arbitrage opportunity exists on Coinbase Pro.

    INPUTS
    - currencies: a list containing the preferred currencies to be used in arbitrage detection

    OUTPUTS
    - cycle: a list containing the arbitrage currencies cycle (will be empty if a cycle is NOT detected)
    - order_book: a dictionary containing the current order size and price, with currency pairs as keys"""

    # Retrieve the existing currencies and their corresponding currency pairs that will define the directed graph
    nodes, edges = coinbase_process_nodes_and_edges(currencies)

    # Create the directed graph
    graph, order_book = coinbase_graph(nodes, edges)

    # Find a negative cycle to identify an arbitrage opportunity, if exists
    arbitrage = bellman_ford(graph)

    # Create an empty list to store the potential arbitrage cycle
    cycle = []

    if not arbitrage:
        print('No arbitrage opportunity detected!')
    else:
        # Retrieve the currencies in the arbitrage cycle, in order
        for index in arbitrage:
            cycle.append(nodes[index])

    return cycle, order_book


def coinbase_arbitrage_pairs(cycle):
    """Retrieves the currency pairs involved in the arbitrage opportunity, along with order type, as they appear in the cycle.

    INPUTS
    - cycle: a list containing the currencies in the arbitrage cycle in order

    OUTPUTS
    - arbitrage_pairs: a list of tuples containing (arbitrage currency pair, type of order) as they appear in the cycle"""

    # Number of currencies in the cycle
    n = len(cycle)

    # Create an empty list to store the currency pairs in the arbitrage opportunity, along with order type, as they appear in the cycle 
    arbitrage_pairs = []

    # Retrieve all of the existing currency pairs on Coinbase Pro
    existing_pairs = coinbase_currency_pairs()

    # Iterate through the arbitrage cycle currencies to establish the relevant currency pairs
    for index, currency in enumerate(cycle):

        # The currency pairs are added to arbitrage_pairs in order of appearance in the arbitrage cycle, along with the type of order - buy or sell
        if currency + '-' + cycle[(index + 1) % n] in existing_pairs:
            arbitrage_pairs.append((currency + '-' + cycle[(index + 1) % n], 'sell'))
        if cycle[(index + 1) % n] + '-' + currency in existing_pairs:
            arbitrage_pairs.append((cycle[(index + 1) % n] + '-' + currency, 'buy'))

    return arbitrage_pairs


def coinbase_currency_increment_info(arbitrage_pairs):
    """Retrieves quote_increment and base_increment from Coinbase Pro for each currency pair in the arbitrage cycle.

    INPUTS
    - arbitrage_pairs: a list containing tuples (arbitrage currency pair, type of order) as they appear in the cycle

    OUTPUTS
    - increment_info: a dictionary containing quote_increment and base_increment in dictionaries, with currency pairs as keys"""

    # Create an empty dictionary to store the information
    increment_info = {}

    # Extract the arbitrage pair names from arbitrage_pairs list
    arbitrage_pairs_list = [i[0] for i in arbitrage_pairs]

    # Iterate through all the existing currency pairs to extract the required information
    for item in coinbase.get_pairs():

        if item['id'] in arbitrage_pairs_list:
            # Add quote_increment and base_incremement to the dictionary, with currency pair as key
            increment_info[item['id']] = {'quote_increment': item['quote_increment'],
                                        'base_increment': item['base_increment']}

    return increment_info


def coinbase_filter_orders_info(cycle, orders):
    """Extracts all the necessary information for calculation of maximum profit order sizes in the arbitrage cycle.

    INPUTS
    - cycle: a list containing the arbitrage cycle (will be empty if a cycle is NOT detected)
    - orders: a dictionary containing the current order sizes and prices for all currency pairs, with currency pairs as keys

    OUTPUTS
    - cycle: a list containing the arbitrage cycle currencies in order
    - arbitrage_pairs: a list containing tuples (arbitrage currency pair, type of order) in order of appearance in currencies
    - arbitrage_orders: a dictionary containing the order size and price, with currency pairs as keys
    - increment_info: a dictionary containing quote_increment and base_increment in dictionaries, with currency pairs as keys"""

    # Find the arbitrage currency pairs using coinbase_arbitrage_pairs
    arbitrage_pairs = coinbase_arbitrage_pairs(cycle)
    currency_pairs = [i[0] for i in arbitrage_pairs] # Extract the names of the currency pairs

    # Create a dictionary to store the order size and price of each arbitrage currency pair
    arbitrage_orders = {}

    # Retrieve quote_increment and base_increment values for each currency pair
    increment_info = coinbase_currency_increment_info(arbitrage_pairs)

    # Iterate through orders to extract the relevant order information for the arbitrage cycle
    for pair in orders:
        if pair in currency_pairs:
            arbitrage_orders[pair] = orders[pair]

    return cycle, arbitrage_pairs, arbitrage_orders, increment_info


def coinbase_print_order_sequence(arbitrage_pairs, arbitrage_orders, increment_info, transaction_fee, maximum_order_sizes):
    """Prints a detailed order sequence for the arbitrage opportunity.
    
    INPUTS
    - arbitrage_pairs: a list containing tuples (arbitrage currency pair, type of order) in order of appearance in currencies
    - arbitrage_orders: orders: a dictionary containing the order size and price, with currency pairs as keys
    - increment_info: a dictionary containing all the relevant information in dictionaries, with currency pairs as keys
    - transaction_fee: a float representing the Coinbase Pro taker fee per order as a percentage
    - maximum_order_sizes: a list containing the maximum possible order sizes for each currency pair in the arbitrage cycle"""
    
    for count, data_store in enumerate(arbitrage_pairs):
        
        pair, order_type = data_store # Unpack the tuple
        index = pair.index('-')

        # Retrieve the quote_increment and base_increment values; these vary for each currency pair
        base_precision = abs(int(np.log10(eval(increment_info[pair]['base_increment']))))
        quote_precision = abs(int(np.log10(eval(increment_info[pair]['quote_increment']))))
        
        # Deal with case if the order is 'sell', ie: BASE --> QUOTE
        if order_type == 'sell':
            price = eval(arbitrage_orders[pair]['b_price'])
            print('Sell {base}, to get {quote}, via an order of {size} {base} at price of {price} {quote}, to get {amount} {quote} by selling {size} {base}, with a fee of {fee} {quote}.'.format(
                    base=pair[:index], quote=pair[index + 1:],
                    size=round(maximum_order_sizes[count], base_precision), price=round(price, quote_precision),
                    amount=round(maximum_order_sizes[count] * price * (100 - transaction_fee) / 100, quote_precision),
                    fee=round(maximum_order_sizes[count] * price * transaction_fee / 100, quote_precision)))
            
        # Deal with case if the order is 'buy', ie: QUOTE --> BASE
        else:
            price = eval(arbitrage_orders[pair]['a_price'])
            print('Buy {base}, using {quote}, via an order of {size} {base} at price of {price} {quote}, to get {amount} {base} at cost of {cost} {quote}, with a fee of {fee} {quote}.'.format(
                    base=pair[:index], quote=pair[index + 1:],
                    size=round(maximum_order_sizes[count], base_precision), price=round(price, quote_precision),
                    amount=round(maximum_order_sizes[count], base_precision),
                    cost=round(maximum_order_sizes[count] * price, quote_precision),
                    fee=round(maximum_order_sizes[count] * price * transaction_fee / 100, quote_precision)))
            

def coinbase_order_size(cycle, arbitrage_pairs, arbitrage_orders, increment_info, transaction_fee, balance, order_sequence=False):
    """Calculates the maximum order size with respect to each currency pair in the arbitrage opportunity if an overall profit can be achieved.

    INPUTS
    - cycle: a list containing the arbitrage cycle currencies in order
    - arbitrage_pairs: a list containing tuples (arbitrage currency pair, type of order) in order of appearance in currencies
    - arbitrage_orders: orders: a dictionary containing the order size and price, with currency pairs as keys
    - increment_info: a dictionary containing all the relevant information in dictionaries, with currency pairs as keys
    - transaction_fee: a float representing the Coinbase Pro taker fee per order as a percentage
    - balance: a dictionary containing the available balances on Coinbase Pro, with currencies as keys
    - order_sequence: (optional) if True, prints information about each order to the screen

    OUTPUTS
    - maximum_order_sizes: a list containing the maximum possible order sizes for each currency pair in the arbitrage cycle
    - balance: a dictionary containing the (updated) balances on Coinbase Pro, with currencies as keys"""

    # Get the number of currencies in the arbitrage cycle
    n = len(cycle)

    # Initialize a ndarray to store the order sizes
    maximum_order_sizes = np.zeros(n, dtype=np.float64)

    # Retrieve the available balance of the starting currency in the arbitrage cycle
    x = balance[cycle[0]]

    # Initialize a ndarray to store the precision values of base currencies involved in each order
    base_currency_precision = np.zeros(n, dtype=np.int8)

    # Iterate through arbitrage_pairs to determine the maximum possible order sizes for each currency pair
    for count, data_store in enumerate(arbitrage_pairs):
        
        # Unpack the data_store tuple
        pair, order_type = data_store

        # Update the precision value of the base currency in base_currency_precision
        base_currency_precision[count] = abs(int(np.log10(eval(increment_info[pair]['base_increment']))))

        # Deal with case if the order is 'sell', ie: BASE --> QUOTE
        if order_type == 'sell':

            price = eval(arbitrage_orders[pair]['b_price'])  # Best bid price
            size = eval(arbitrage_orders[pair]['b_size'])  # Best bid order size

            if x <= size:
                maximum_order_sizes[count] = x  # Assign the maximum order amount to maximum_order_sizes
                x *= price  # Update the quote currency amount received
            else:  # If x > order
                maximum_order_sizes *= (size / x)  # Readjust the previous maximum order amounts in maximum_order_sizes
                maximum_order_sizes[count] = size  # Assign the maximum order amount to maximum_order_sizes
                x = size * price  # Update the quote currency amount received

            x *= (100 - transaction_fee) / 100  # Adjust amount after transaction fee has been deducted

        # Deal with case if it the order is 'buy', ie: QUOTE --> BASE
        else:
            
            price = eval(arbitrage_orders[pair]['a_price'])  # Best ask price
            size = eval(arbitrage_orders[pair]['a_size'])  # Best ask order size

            x /= (1 + (transaction_fee / 100))  # Adjust amount after transaction fee has been deducted

            if x <= (size * price):
                maximum_order_sizes[count] = x / price  # Assign the maximum order amount to maximum_order_sizes
                x /= price  # Update the base currency amount received
            else:  # If x > (order * price)
                maximum_order_sizes *= ((size * price) / x)  # Readjust the previous maximum order amounts in maximum_order_sizes
                maximum_order_sizes[count] = size  # Assign the maximum order amount to maximum_order_sizes
                x = size  # Update the base currency amount received

    # Correct maximum_order_sizes for base currency precision
    for index in range(n): 
        maximum_order_sizes[index] = round(maximum_order_sizes[index], base_currency_precision[index])
    
    # Determine the precision of value x
    # Deal with case if final order is a 'sell' in the arbitrage cycle, ie: BASE --> QUOTE
    if arbitrage_pairs[-1][1] == 'sell':
        precision_final = abs(int(np.log10(eval(increment_info[arbitrage_pairs[-1][0]]['quote_increment'])))) # Quote currency precision
    # Deal with case if final order is a 'buy' in the arbitrage cycle, ie: QUOTE --> BASE
    else:
        precision_final = abs(int(np.log10(eval(increment_info[arbitrage_pairs[-1][0]]['base_increment'])))) # Base currency precision
    
    # Calculate the profit made via the arbitrage opportunity
    # Deal with case if initial order is 'sell' in the arbitrage cycle, ie: BASE --> QUOTE
    if arbitrage_pairs[0][1] == 'sell':
        precision_init = abs(int(np.log10(eval(increment_info[arbitrage_pairs[0][0]]['base_increment'])))) # Base currency precision
        profit = round(x, precision_final) - round(maximum_order_sizes[0], precision_init)
    # Deal with case if initial order is 'buy' in the arbitrage cycle, ie: QUOTE --> BASE
    else:
        precision_init = abs(int(np.log10(eval(increment_info[arbitrage_pairs[0][0]]['quote_increment'])))) # Quote currency precision
        price = eval(arbitrage_orders[arbitrage_pairs[0][0]]['a_price'])
        profit = round(x, precision_final) - round((maximum_order_sizes[0] * price), precision_init)

    # Check if the arbitrage opportunity is profitable
    if profit <= 0:
        print('An arbitrage opportunity was detected, but it was unprofitable!')
        return None, balance

    # Calculate the new account balance value, after the arbitrage cycle has been executed
    updated_balance = round(balance[cycle[0]], precision_init) + profit
    
    # If order_sequence is True, call coinbase_print_order_sequence to print the order sequence
    if order_sequence: coinbase_print_order_sequence(arbitrage_pairs, arbitrage_orders, increment_info, transaction_fee, maximum_order_sizes)
    
    # Print a summary of the profit made with the arbitrage opportunity
    print('A profit of {profit} {currency} was made, with initial balance at {start} {currency} and updated balance at {end} {currency}'.format(
            profit=round(profit, max(precision_init, precision_final)), start=round(balance[cycle[0]], precision_init),
            end=round(updated_balance, max(precision_init, precision_final)), currency=cycle[0]))

    # Update the account balances on Coinbase Pro
    balance[cycle[0]] = round(updated_balance, max(precision_init, precision_final))

    return maximum_order_sizes, balance


def coinbase_main(currencies, transaction_fee, balance):
    """Given a list of currency codes to be used in arbitrage detection and available balances on Coinbase Pro, prints the order sequence 
    if a profitable arbitrage opportunity is detected and outputs the updated balances. 

    INPUTS
    - currencies: a list containing the preferred currencies to be used in arbitrage detection
    - transaction_fee: a float representing the Coinbase Pro taker fee per order as a percentage
    - balance: a dictionary containing the available balances on Coinbase Pro, with currencies as keys

    OUTPUTS
    - balances: a dictionary containing the (updated) balances on Coinbase Pro, with currencies as keys"""

    # Establish if an arbitrage opportunity exists
    cycle, order_book = coinbase_arbitrage(currencies)

    # If an arbitrage opportunity exists, determine if it is profitable; and if so, output the maximum possible order sizes that can be placed 
    if cycle:
        # Gather the information required for calculation of order sizes
        cycle, arbitrage_pairs, arbitrage_orders, increment_info = coinbase_filter_orders_info(cycle, order_book)

        # If arbitrage opportunity is profitable, output the maximum_order_sizes and the updated balance
        maximum_order_sizes, balance = coinbase_order_size(cycle, arbitrage_pairs, arbitrage_orders, increment_info, transaction_fee, balance, order_sequence=True)

    return balance
