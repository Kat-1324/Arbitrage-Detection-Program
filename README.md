# Arbitrage Detection System for Coinbase Pro


This project was created as a learning exercise for algorithmic trading in Python. The program detects **arbitrage** on the [Coinbase Pro](https://pro.coinbase.com/) exchange by implementing the **Bellman-Ford algorithm**. If a valid and profitable arbitrage opportunity is found, the program prints an order sequence and overall profit to the console. 

#### Brief Summary

* For each currency pair, exchange rates are calculated using the best bid and best ask prices from the corresponding **live order books**. 
* A weighted directed graph is constructed to model the exchange - nodes represent individual currency codes, edges represent a currency pair relationship and weights represent the linearized exchange rates for each currency pair relationship.
* The Bellman-Ford algorithm is applied to the digraph to establish if a negative cycle exists (this implies that there is arbitrage).
* If the arbitrage is valid (satisfies the notional minimum limit requirement) and yields a positive profit (accounting for the taker fees per each order and the base currency precision), the maximum possible order size for each currency pair in the arbitrage cycle is printed to the console, along with the final profit. 

# Quick Start

#### How do I launch the system?

Access  `main.py` in the repository. Adjust the `currencies` and `tradedVolume` variables if desired (example values have already been provided in `main.py`). Run the program.

#### What are the input variables in `main.py`?

* **client:** an exchange client object. Currently only access to Coinbase Pro is supported by the system.

```python
from clients.coinbase.coinbase_client import CoinbaseClient

client = CoinbaseClient()
```

* **currencies:** a list of currency codes that should be used by the arbitrage detection algorithm. There is no limit on the number of currency codes. 

```python
currencies = ['ETH', 'BTC', 'USD', 'BADGER', 'FOX', 'EUR']
```

* **tradedVolume:** a float or an integer. The [fee tier](https://help.coinbase.com/en/pro/trading-and-funding/trading-rules-and-fees/fees) on Coinbase Pro is based on the user's total USD trading volume over the trailing 30-day period. An additional pricing tier ($10,000,000,000+) has been added to the system that facilitates no transaction fees per order - this has been done for experimenting purposes and is not a valid pricing tier on Coinbase Pro.

```python
tradedVolume = 100000000000
```

#### What outputs should I expect from `main.py`?

* If it is impossible for arbitrage to ever occur given the input currency codes, the program will print **"Given the currencies and the client, it is not possible to get an arbitrage."** to the console. Please proceed to provide a new list of currency codes so that arbitrage could be detected.
* If no arbitrage is detected, the program will print **"No arbitrage has been found."** to the console.
* If an arbitrage is detected, but the maximum order sizes do not satisfy the notional minimum limit requirement, the program will print **"An arbitrage has been found. It does NOT satisfy the notional minimum limit requirements."** to the console.
* If an arbitrage is detected and the maximum order sizes satisfy the notional minimum limit requirement, but the profit is non-positive (due to transaction fees and order size correction for base currency precision), the program will print **"An arbitrage has been found. It satisfies the notional minimum limit requirements. It makes NO profit."** to the console.
* If an arbitrage is detected and the maximum order sizes satisfy the notional minimum limit requirement and yields a positive profit, the program will print the **order sequence** and **profit** made via arbitrage to the console.


# Python Version

I recommend Python 3.7. The code will also work with Python 3.6, as it is the minimum supported version for NumPy use.  
