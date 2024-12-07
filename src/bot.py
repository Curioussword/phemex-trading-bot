import ccxt

import pandas as pd

import time

from datetime import datetime

from utils import load_config

from exchange_setup import initialize_exchange

from indicators import calculate_vwap, calculate_ema

from state_manager import StateManager, get_positions_details





# Load configuration

config = load_config()

phemex_futures = initialize_exchange()

state_manager = StateManager(phemex_futures)

MAX_SIZE = config['trade_parameters']['max_size']

# Set leverage

phemex_futures.set_leverage(45, 'BTC/USD:BTC')


def fetch_live_data(symbol, limit=20):

    """Fetch live market data from Phemex and format it as a DataFrame."""

    try:

        # Current timestamp in milliseconds

        current_time = int(time.time() * 1000)

        timeframe_ms = 60 * 1000  # 1 minute in milliseconds

        since = current_time - (limit * timeframe_ms)

        

        # Fetch OHLCV data

        ohlcv = phemex_futures.fetch_ohlcv(symbol, timeframe='1m', since=since)


        data = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

        

        return data



    except Exception as e:

        print(f"[ERROR] Failed to fetch live data: {e}")

        return pd.DataFrame()




def calculate_tp_sl(order_type, current_price):

    """Calculate Take Profit and Stop Loss prices."""

    tp_percentage = 0.01  # 1% Take Profit

    sl_percentage = 0.01  # 1% Stop Loss



    if order_type == "SELL":

        take_profit_price = current_price * (1 - tp_percentage)

        stop_loss_price = current_price * (1 + sl_percentage)

    elif order_type == "BUY":

        take_profit_price = current_price * (1 + tp_percentage)

        stop_loss_price = current_price * (1 - sl_percentage)



    return round(take_profit_price, 3), round(stop_loss_price, 2)




def execute_trade(order_type, amount, config, current_price, exchange):

    """Execute a trade with retry and error handling."""

    try:

        symbol = config['trade_parameters']['symbol']

        total_size, position_details = get_positions_details(exchange, symbol)



        # Check if adding this trade exceeds MAX_SIZE

        if total_size + amount > MAX_SIZE:

            print(f"[WARNING] Max size exceeded. Current total: {total_size}, Attempted: {amount}, Max: {MAX_SIZE}")

            return



        take_profit_price, stop_loss_price = calculate_tp_sl(order_type, current_price)

        limit_price = round(current_price * (0.99 if order_type == "SELL" else 1.01), 5)



        print(f"[DEBUG] Setting Take Profit at {take_profit_price}")

        print(f"[DEBUG] Setting Stop Loss at {stop_loss_price}")

        print(f"[DEBUG] Setting Limit Price at {limit_price}")



        # Try placing a limit order

        try:

            order = exchange.create_order(

                symbol=symbol,

                type="limit",

                side=order_type.lower(),

                amount=amount,

                price=limit_price,

                params={"ordType": "Limit"}

            )

            print("[INFO] Limit order placed. Waiting for execution...")

            time.sleep(2)



            # Check if the order was filled

            order_status = exchange.fetch_order(order['id'], symbol)

            if order_status.get('status') != 'closed':

                print("[INFO] Limit order not filled. Canceling and retrying as market order...")

                exchange.cancel_order(order['id'], symbol)

                order = exchange.create_order(

                    symbol=symbol,

                    type="market",

                    side=order_type.lower(),

                    amount=amount,

                    params={"ordType": "Market"}

                )

        except Exception as e:

            print(f"[ERROR] Error placing limit order: {e}")

            print("[INFO] Switching to market order...")

            order = exchange.create_order(

                symbol=symbol,

                type="market",

                side=order_type.lower(),

                amount=amount,

                params={"ordType": "Market"}

            )



        # Place Stop Loss and Take Profit orders

        tp_sl_side = "buy" if order_type == "SELL" else "sell"

        exchange.create_order(

            symbol=symbol,

            type="stop",

            side=tp_sl_side,

            amount=amount,

            price=stop_loss_price,

            params={"ordType": "Stop", "stopPx": stop_loss_price}

        )



        exchange.create_order(

            symbol=symbol,

            type="limit",

            side=tp_sl_side,

            amount=amount,

            price=take_profit_price,

            params={"ordType": "LimitIfTouched", "stopPx": take_profit_price}

        )



        print(f"Trade executed successfully: Size: {amount}, Symbol: {symbol}, ID: {order.get('id', 'N/A')}")

        log_trade(order_type, amount, current_price, order)



    except Exception as main_error:

        print(f"[ERROR] Critical error in execute_trade: {main_error}")




def log_trade(order_type, amount, price, order=None):

    """Log trade details."""

    global last_trade  



    trade_data = {

        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "order_type": order_type,

        "amount": amount,

        "price": price,

        "status": "executed" if order else "simulated",

        "PnL": 0

    }



    if last_trade and last_trade["order_type"] != order_type:

        if order_type == "SELL":

            trade_data["PnL"] = (price - last_trade["price"]) * amount

        elif order_type == "BUY":

            trade_data["PnL"] = (last_trade["price"] - price) * amount

        

        print(f"[TRADE] {order_type} at {price} with amount {amount}. PnL: {trade_data['PnL']:.2f}")



    last_trade = trade_data

    trade_log.append(trade_data)



    cumulative_PnL = sum(trade["PnL"] for trade in trade_log)

    print(f"[SUMMARY] Cumulative PnL: {cumulative_PnL:.2f}")



    if order:

        print("\n=== Live Order Details ===")

        print(f"Order Type: {order_type}")

        print(f"Status: {order['info'].get('status', 'N/A')}")

        print(f"Order ID: {order['id']}")

        print(f"Symbol: {order['symbol']}")

        print(f"Price: {order.get('price', 'N/A')}")

        print(f"Amount: {order['amount']}")

        print(f"Average Executed Price: {order.get('average', 'N/A')}")

        print(f"Filled: {order['filled']}")

        print(f"Remaining: {order['remaining']}")

        print(f"Order Status: {order['status']}")

        print("=== End of Order Details ===\n")
