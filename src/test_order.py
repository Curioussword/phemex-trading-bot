import ccxt

import yaml

import os



def load_config():

    """Load the configuration file."""

    with open(os.path.join(os.path.dirname(__file__), '../config/config.yaml'), 'r') as file:

        config = yaml.safe_load(file)

    return config



config = load_config()

phemex_futures = ccxt.phemex({

    'apiKey': config['phemex']['api_key'],

    'secret': config['phemex']['api_secret'],

    'urls': {

        'api': {

            'public': config['phemex']['urls']['api']['public'],

            'private': config['phemex']['urls']['api']['private'],

        }

    },

    'enableRateLimit': True,

    'options': {

        'defaultType': 'future'

    }

})



def test_order():

    try:

        symbol = "BTCUSD"

        order_type = "market"

        side = "buy"

        amount = 100  # Very small amount to minimize cost



        print(f"Attempting to place a test {side.upper()} order for {amount} {symbol}...")

        order = phemex_futures.create_order(symbol=symbol, type=order_type, side=side, amount=amount)

        print("Order successfully placed:", order)

    except Exception as e:

        print(f"Error placing test order: {e}")



if __name__ == "__main__":

    test_order()
