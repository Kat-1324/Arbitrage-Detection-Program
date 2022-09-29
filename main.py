from main_implementation import main
from clients.coinbase.coinbase_client import CoinbaseClient

client = CoinbaseClient()
currencies = ['ETH', 'BTC', 'USD', 'EUR', 'ALGO', 'BADGER']
tradedVolume = 100000000000000

main(client, currencies, tradedVolume)
