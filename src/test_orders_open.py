
import ccxt

import yaml

import os




def load_config():

    """Load the configuration file."""

    with open(os.path.join(os.path.dirname(__file__), '../config/config.yaml'), 'r') as file:

        config = yaml.safe_load(file)

    return config



# Load configuration

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



all_orders = exchange.fetch_all_orders()

open_orders = [order for order in all_orders if order['status'] == 'open']

num_open_orders = len(open_orders)
