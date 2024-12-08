import pandas as pd



def calculate_vwap(data):

    if "close" not in data.columns or "volume" not in data.columns:

        raise ValueError("Data missing required columns for VWAP calculation.")

    #Ensures no zero or nan values
    data["price_volume"] = data["close"] * data["volume"]

    vwap = data["price_volume"].cumsum() / data["volume"].cumsum()

    return vwap



def calculate_ema(data, period):
    """Calculate Exponential Moving Average (EMA)"""
    return data['close'].ewm(span=period, adjust=False).mean()



# Calculate ATR over a rolling period
def calculate_atr(data, period=14):
    """
    Calculate the Average True Range (ATR) indicator based on historical data.

    """
    # Calculate True Range
    data['HL'] = data['high'] - data['low']
    data['HC'] = abs(data['high'] - data['close'].shift())
    data['LC'] = abs(data['low'] - data['close'].shift())
    data['TR'] = data[['HL', 'HC', 'LC']].max(axis=1)

    # Calculate the rolling average of TR over the 'period' days

    data['ATR'] = data['TR'].rolling(window=period).mean()

    # Return the most recent ATR value

    return data['ATR'].iloc[-1]
