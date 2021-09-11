# Crypto Arbitrage Detection System on Coinbase Pro


This project was created as a learning exercise for algorithmic trading in Python. The program detects **crypto arbitrage opportunities** on the [Coinbase Pro](https://pro.coinbase.com/) exchange by implementing the **Bellman-Ford algorithm**. If a profitable arbitrage opportunity is found, the program prints the maximum possible order size that can be used for each trade and the overall profit to the console. 

#### Brief Summary

* For each currency pair, exchange rates are calculated using the best bid and best ask prices from the corresponding **live order books**. 
* A directed graph is constructed with nodes representing individual currencies, edges representing a currency pair relationship and weights representing the linearized exchange rates for each currency pair relationship. 
* The Bellman-Ford Algorithm is applied to the directed graph to establish if a negative cycle exists (this signals an arbitrage opportunity).
* If the arbitrage opportunity yields a profit (taking into account the taker transaction fees per each order), the maximum possible order size for each currency pair in the arbitrage cycle is printed to the console, along with the generated profit. 

# Quick Start


#### How do I launch the system?

Access  `main.py` in the repository. Uncomment all the lines. Provide input values for `currencies`, `transaction_fee` and `balance` (these are explained further below); then run the program. 

Example input values have already been provided in `main.py` if you want to see how the program works; simply uncomment all the lines and run the program. 

#### What inputs should I give to `main.py`?

* **currencies:** a list of currency codes that you would like to be used in the arbitrage detection algorithm. There is no limit on the number of currencies, and they can be written in any order. For example, if you would like to detect arbitrage opportunities between Bitcoin (BTC), Ethereum (ETH) and US Dollar (USD):

```python
currencies = ['ETH', 'BTC', 'USD']
```

* **transaction_fee:** a float representing the taker transaction fee percentage charged per each order. For example, if a 0.02% transaction fee is applied per each order:

```python
transaction_fee = 0.02
```

* **balance:** a dictionary containing your available balances on Coinbase Pro, ready for use should an arbitrage opportunity arise. The keys are currency codes; the values are the available balances. For example, if you have 0.98 BTC, 1000 USD and 500 ETH available for trading on Coinbase Pro:

```python
balance = {'BTC': 0.98, 'USD': 1000, 'ETH': 500}
```

#### What outputs should I expect from `main.py`?

* If no arbitrage is detected, the program will print **"No arbitrage opportunity detected!"** to the console.
* If an arbitrage is detected, but is unprofitable (defined as a loss being made after taker transaction fees have been applied), the program will print  **"An arbitrage opportunity was detected, but it was unprofitable!"** to the console. 

* If an arbitrage is detected and yields a profit (defined as a positive gain being made after taker transaction fees have been applied), the program will print the **order sequence** and **overall profit** made via the arbitrage opportunity to the console.

**NOTE:** The program **always** returns the (updated) balance, irrespective of whether a profitable arbitrage opportunity was found or not.

# Python Version

I recommend Python 3.7. The code will also work with Python 3.6, as it is the minimum supported version for NumPy use.  
