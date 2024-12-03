import ccxt
import yaml
import os

def load_config():
    """Load the configuration file."""
    with open(os.path.join(os.path.dirname(__file__), '../config/config.yaml'), 'r') as file:
        config = yaml.safe_load(file)
    return config

def print_demo_symbols():
    config = load_config()

    # Initialize phemex  futures instance with demo environment URLs
    phemex_futures = ccxt.phemex({
        'apiKey': config['phemex']['api_key'],
        'secret': config['phemex']['api_secret'],
        'urls': {
            'api': {
                'public': 'https://testnet-api.phemex.com',
            }
        }
    })

    try:
        markets = phemex_futures.load_markets()
        print("Available symbols on phemex Futures Demo:")
        for symbol in markets:
            print(symbol)
    except Exception as e:
        print(f"Error fetching symbols from phemex Futures Demo: {e}")

if __name__ == "__main__":
    print_demo_symbols()
