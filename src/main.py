import ccxt

import pandas as pd

import time

from datetime import datetime

from exchange_setup import initialize_exchange, load_config

from indicators import calculate_vwap, calculate_ema

from state_manager import StateManager

from bot import fetch_live_data, execute_trade



def main():

    global trade_log, last_trade

    trade_log = []

    last_trade = None

    #load configuration
    config = load_config()

    # Initialize the Phemex exchange using the utility function

    phemex_futures = initialize_exchange()


    # Create a StateManager instance with the initialized exchange

    state_manager = StateManager(phemex_futures)



    while True:  # Run continuously

        open_positions = state_manager.get_open_positions()



        if len(open_positions) == 0 and len(trade_log) < config['trade_parameters']['max_orders_per_day']:

            data = fetch_live_data(config['trade_parameters']['symbol'])



            if data.empty:

                print("[ERROR] No data fetched. Retrying...")

                time.sleep(60)

                continue



            vwap = calculate_vwap(data)

            ema_200 = calculate_ema(data, period=200)

            ema_20 = calculate_ema(data, period=20)

            current_price = data["close"].iloc[-1]



            print(f"\n[MARKET STATUS] Current Price: {current_price}")

            print(f"VWAP: {vwap.iloc[-1]}, EMA 200: {ema_200.iloc[-1]}, EMA 20: {ema_20.iloc[-1]}")



            if (vwap.iloc[-1] >= ema_200.iloc[-1] and ema_200.iloc[-1] >= ema_20.iloc[-1]):

                print("SELL condition met, executing sell order...")

                execute_trade("SELL", config['trade_parameters']['order_amount'], config, current_price)

            elif (ema_20.iloc[-1] >= ema_200.iloc[-1]):

                print("BUY condition met, executing buy order...")

                execute_trade("BUY", config['trade_parameters']['order_amount'], config, current_price)

        else:

            print("Open positions exist or max trades reached. Monitoring...")



        state_manager.check_and_display_positions()

        time.sleep(60)  # Check every 60 seconds



if __name__ == "__main__":

    main()
