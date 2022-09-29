"""
Website: https://exchange.coinbase.com/markets contains all relevant information.
         https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getaccounts-1
"""

from clients.base.base_client import BaseClient

import numpy as np


class CoinbaseInterface:
    # https://docs.cloud.coinbase.com/exchange/docs

    def __init__(self, api_url="https://api.pro.coinbase.com"):
        self._publicClient = BaseClient(api_url)

    def getTime(self):
        return self._publicClient.send_message('get', '/time')

    # https://api.exchange.coinbase.com/currencies/{currency_id}
    def getCurrency(self, currency_id):
        return self._publicClient.send_message('get', '/currencies/{}'.format(currency_id))

    #  https://api.exchange.coinbase.com/products/{product_id}
    def getProduct(self, product_id):
        return self._publicClient.send_message('get', '/products/{}'.format(product_id))

    # https://api.exchange.coinbase.com/products/{product_id}/book
    def getOrderBook(self, product_id, level=1):
        return self._publicClient.send_message('get', '/products/{}/book'.format(product_id), params={'level': level})

    def closeSession(self):
        self._publicClient.close()


class CoinbaseClient:
    """ A Coinbase Pro client. """

    def __init__(self):
        self.coinbaseClient = CoinbaseInterface()

    def getTime(self):
        """ Get server time. """
        return self.coinbaseClient.getTime()

    def getOrderBook(self, base, quote):
        """ Get order book w.r.t. specified currency pair.

        PARAMETERS
        ----------
        - base (str): base currency
        - quote (str): quote currency

        RETURN
        ------
        - (dict): contains best bid/ask - price, size and number of orders
        """
        return self.coinbaseClient.getOrderBook(base + '-' + quote)

    def getNotionalMinLimit(self, base, quote):
        """
        Get notional minimum limit for currency pair.

        PARAMETERS
        ----------
        - base (str): base currency
        - quote (str): quote currency

        RETURN
        ------
        - (str): notional minimum limit
        """
        return self.coinbaseClient.getProduct(base + '-' + quote)['min_market_funds']

    @staticmethod
    def getFees(tradedVolume):
        """
        Calculate fee on Coinbase Pro. Assume all orders are charged taker fees.

        PARAMETERS
        ----------
        - tradedVolume (float/int): 30-day USD trading volume

        RETURN
        ------
        - fee (str): fee charged per each trade
        """
        fees = [[10000000000, '0'],  # This fee has been added for testing/experiment purposes - is NOT true for Coinbase Pro
                [400000000, '0.0005'],
                [250000000, '0.0008'],
                [75000000, '0.0012'],
                [15000000, '0.0016'],
                [1000000, '0.0018'],
                [100000, '0.0020'],
                [50000, '0.0025'],
                [10000, '0.0040'],
                [0, '0.0060']]
        for limit, fee in fees:
            if tradedVolume >= limit:
                return fee

    def getBasePrecision(self, base, quote):
        """
        Get base currency increment precision.

        PARAMETERS
        ----------
        - base (str): base currency
        - quote (str): quote currency

        RETURN
        ------
        - (int): precision given as the power of 10
        """
        return self._getPrecision(eval(self.coinbaseClient.getProduct(base + '-' + quote)['base_increment']))

    @staticmethod
    def _getPrecision(decimal):
        """
        Finds the exponent of a power of 10.
        """
        return int(np.log10(decimal))

    def checkCurrenciesExistence(self, currencies):
        """
        Check if all given currency codes exist on the exchange. Raises a CurrencyNotFound exception if not.
        Not all currencies may be currently in use for trading on Coinbase Pro.

        PARAMETERS
        ----------
        - currencies (list/tuples): currency codes to be checked
        """
        currenciesNotFound = []

        for ccy in currencies:
            currencyInfo = self.coinbaseClient.getCurrency(ccy)

            if currencyInfo['message'] == 'NotFound':
                currenciesNotFound.append(ccy)
            elif currencyInfo['message'] == '' and currencyInfo['status'] != 'online':
                currenciesNotFound.append(ccy)

        if len(currenciesNotFound) != 0:
            raise CurrencyNotFound(currenciesNotFound)

    def checkCurrencyPairExistence(self, base, quote):
        """
        Checks if given currency pair is traded on the exchange.

        PARAMETERS
        ----------
        - base (str): base currency
        - quote (str): quote currency

        RETURN
        ------
        - True or False (Boolean): True if currency pair exists on exchange else False
        """
        try:
            if self.coinbaseClient.getProduct(base + '-' + quote)['message'] == 'NotFound':
                return False
        except KeyError:
            return True

    def closeSession(self):
        """
        Closes session, or in other words, closes connection to the exchange.
        """
        self.coinbaseClient.closeSession()


        ####################################################
        ##                  HELPER CLASS                  ##
        ####################################################


class CurrencyNotFound(Exception):

    def __init__(self, currencies):
        self.currencies = currencies

    def __str__(self):
        return "The following currency ID(s) are not available on the exchange: " + ", ".join(self.currencies)
