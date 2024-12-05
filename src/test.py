import ccxt

import pandas as pd

import yaml

import os



def load_config():

    """Load the configuration file."""

    config_path = os.path.join(os.path.dirname(__file__), '../config/config.yaml')

    if not os.path.exists(config_path):

        print(f"[ERROR] Config file not found at {config_path}")

        return {}

    

    with open(config_path, 'r') as file:

        config = yaml.safe_load(file)

    print(f"[DEBUG] Loaded config: {config}")

    return config



config = load_config()



# Initialize the exchange (Phemex in this case)

exchange = ccxt.phemex({

    'apiKey': config['phemex']['api_key'],

    'secret': config['phemex']['api_secret'],

    'urls': {

        'api': {

            'public': 'https://testnet-api.phemex.com/exchange/public',

            'private': 'https://testnet-api.phemex.com',

        }

    },

    'enableRateLimit': True,

    'options': {

        'defaultType': 'future'  # Specify that we're using futures

    }

})



def fetch_live_data(symbol, limit=20):

    """Fetch live market data from Phemex and format it as a DataFrame."""

    try:

        print(f"[DEBUG] Fetching live data for symbol: {symbol}, limit: {limit}")



        # Initialize Phemex exchange object

        phemex_futures = ccxt.phemex()



        # Ensure the symbol exists in the market

        markets = phemex_futures.load_markets()

        print(f"[DEBUG] Available markets: {list(markets.keys())}")  # Debugging the available markets



        if symbol not in markets:

            raise ValueError(f"Symbol {symbol} not found in available markets.")



        # Fetch OHLCV data

        ohlcv = phemex_futures.fetch_ohlcv(symbol, timeframe='1m', limit=limit)



        # Format data into DataFrame

        data = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])



        return data



    except Exception as e:

        print(f"[ERROR] Failed to fetch live data: {e}")

        return pd.DataFrame()  # Return empty DataFrame on error



if __name__ == "__main__":

    symbol = 'BTC-USD'  # Replace with a valid symbol

    data = fetch_live_data(symbol, limit=20)

    print(data)

