from util.restClient import RestClient


class CoinbaseClient:
    def __init__(self, api_url="https://api.pro.coinbase.com"):
        self._publicClient = RestClient(api_url)

    def get_time(self):
        return self._publicClient.send_message('get', '/time')

    # https://docs.pro.coinbase.com/#products
    def get_pairs(self):
        return self._publicClient.send_message('get', '/products')

    # https://docs.pro.coinbase.com/#get-product-order-book
    def get_order_book(self, product_id, level=1):
        params = {'level': level}
        return self._publicClient.send_message('get',
                                  '/products/{}/book'.format(product_id),
                                  params=params)

    # https://docs.pro.coinbase.com/#currencies
    def get_currencies(self):
        return self._publicClient.send_message('get', '/currencies')