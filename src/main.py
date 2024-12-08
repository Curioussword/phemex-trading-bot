import ccxt

import time

import pandas as pd

from datetime import datetime

from utils import load_config

from exchange_setup import initialize_exchange

from indicators import calculate_vwap, calculate_ema

from state_manager import StateManager

from bot import fetch_live_data, execute_trade



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



    while True:

        try:

            # Fetch live data

            data = fetch_live_data(config['trade_parameters']['symbol'])



            # Verify fetched data

            if data.empty or "close" not in data.columns or data["close"].isna().all():

                print("[ERROR] Data fetch failed or invalid data. Retrying in 60 seconds...")

                time.sleep(60)

                continue



            # Safely assign current_price only after validating live data

            current_price = data["close"].iloc[-1]



            # Check and display open positions only with valid current_price

            state_manager.check_and_display_positions(config['trade_parameters']['symbol'], current_price)



            # Get open positions

            open_positions = state_manager.get_open_positions(config['trade_parameters']['symbol'])



            # Ensure room for new trades

            if len(open_positions) < 5 and len(trade_log) < config['trade_parameters']['max_orders_per_day']:

                # Ensure we have valid live data

                if data.empty:

                    print("[ERROR] Data fetch failed. Retrying in 60 seconds...")

                    time.sleep(60)

                    continue



                # Evaluate market conditions based on the fetched live data

                evaluate_market_conditions(data, config, current_price, phemex_futures)



            else:

                print("Maximum open positions reached or max trades per day reached. Monitoring...")



            # Wait before re-evaluating

            time.sleep(60)



        except KeyboardInterrupt:

            print("Exiting trading bot...")

            break  # Gracefully exit on keyboard interrupt



        except Exception as e:

            print(f"[ERROR] An unexpected error occurred: {e}")

            time.sleep(60)  # Retry after a delay




if __name__ == "__main__":

    main()

