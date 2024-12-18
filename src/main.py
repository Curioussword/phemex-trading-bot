import time

import json

from datetime import datetime

import pandas as pd

import ccxt



from utils import load_config

from exchange_setup import initialize_exchange

from indicators import calculate_vwap, calculate_ema

from state_manager import StateManager

from bot import fetch_live_data, execute_trade



# Function to dynamically evaluate market volatility

def determine_volatility(data):

    """

    Evaluate volatility based on price changes.

    If market is volatile, return 1-minute intervals; otherwise, 5-minute.

    """

    try:

        # Use percentage change in the closing price over the recent history

        recent_close_prices = data["close"]

        # Ensure there are at least N periods of data for calculation

        if len(recent_close_prices) < 5:

            return 5  # Default to 5 minutes if insufficient data

        volatility_measure = abs(recent_close_prices.iloc[-1] - recent_close_prices.iloc[-5]) / recent_close_prices.iloc[-5]

        # Threshold-based volatility measurement (tune the threshold if necessary)

        if volatility_measure > 0.002:  # If >0.2% price change, market is volatile

            return 1  # Switch to 1-minute intervals for fine-grained signals

        else:

            return 5  # Market is stable, stay on 5-minute intervals

    except Exception as e:

        print(f"[ERROR] Error in determine_volatility: {e}")

        return 5  # Default back to 5 minutes if error occurs





def evaluate_market_conditions(data, config, current_price, phemex_futures):

    """

    Evaluate market conditions based on VWAP, EMA 200, and EMA 20 with a Neutral Zone Threshold.

    Executes a trade if conditions are met.

    """

    try:

        # Calculate indicators

        vwap = calculate_vwap(data)

        ema_200 = calculate_ema(data, period=200)

        ema_20 = calculate_ema(data, period=20)



        # Neutral Zone Threshold

        threshold = config['trade_parameters']['neutral_zone_threshold']

        ema_diff = abs(ema_20.iloc[-1] - ema_200.iloc[-1])



        # Log market status for debugging

        print(f"\n[MARKET STATUS] Current Price: {current_price}")

        print(f"VWAP: {vwap.iloc[-1]}, EMA 200: {ema_200.iloc[-1]}, EMA 20: {ema_20.iloc[-1]}")

        print(f"Neutral Zone Threshold: {threshold}, EMA Difference: {ema_diff}")



        # Evaluate trading conditions

        if ema_diff < threshold:

            print("[INFO] Market is within the neutral zone. No trades executed.")

            return  # Skip trading in the neutral zone



        if vwap.iloc[-1] >= ema_200.iloc[-1] and ema_200.iloc[-1] >= ema_20.iloc[-1]:

            print("SELL condition met, executing sell order...")

            execute_trade("SELL", config['trade_parameters']['order_amount'], config, current_price, phemex_futures)

        elif ema_20.iloc[-1] >= ema_200.iloc[-1]:

            print("BUY condition met, executing buy order...")

            execute_trade("BUY", config['trade_parameters']['order_amount'], config, current_price, phemex_futures)

        else:

            print("[INFO] No trade conditions met. Monitoring...")

    except Exception as e:

        print(f"[ERROR] An error occurred in evaluate_market_conditions: {e}")



def main():

    global trade_log, last_trade



    # Initialize global variables

    trade_log = []

    last_trade = None



    # Load configuration and initialize components

    config = load_config()

    phemex_futures = initialize_exchange()

    state_manager = StateManager(phemex_futures)



    # Dynamic timeframe decision defaults

    current_interval = 5  # Default to 5 minutes



    while True:

        try:

            # Fetch live data dynamically

            # Simulate dynamic switching based on market volatility

            data = fetch_live_data(config['trade_parameters']['symbol'], interval=f"{current_interval}m", phemex_futures = phemex_futures)

            if data.empty:

                print("[ERROR] No data fetched. Retrying in 60 seconds...")

                time.sleep(60)

                continue



            # Determine market volatility

            current_interval = determine_volatility(data)



            # Check and display open positions

            state_manager.check_and_display_positions(config['trade_parameters']['symbol'], data['close'].iloc[-1])



            # Get open positions

            open_positions = state_manager.get_open_positions(config['trade_parameters']['symbol'])

            if len(open_positions) < 5 and len(trade_log) < config['trade_parameters']['max_orders_per_day']:

                # Evaluate market conditions dynamically using the most recent live data

                evaluate_market_conditions(data, config, data['close'].iloc[-1], phemex_futures)

            else:

                print("Maximum open positions reached or max trades per day reached. Monitoring...")



            # Wait until next fetch

            time.sleep(60)



        except KeyboardInterrupt:

            print("Exiting trading bot...")

            break



        except Exception as e:

            print(f"[ERROR] An unexpected error occurred: {e}")

            time.sleep(60)  # Retry after a delay



if __name__ == "__main__":

    main()

