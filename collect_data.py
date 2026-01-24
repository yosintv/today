import json
import os
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from tvdatafeed import TvDatafeed, Interval

# 1. Create the data directory if it doesn't exist
folder_path = 'data'
file_path = os.path.join(folder_path, 'value.json')
os.makedirs(folder_path, exist_ok=True)

# Initialize TradingView Connection
tv = TvDatafeed()

def analyze_patterns(df):
    """Detects patterns and returns name + explanation"""
    # Standardize column names for pandas_ta
    df.columns = [x.lower() for x in df.columns]
    
    # Check for specific patterns
    # cdls returns a dataframe where non-zero indicates a pattern found
    patterns = df.ta.cdl_pattern(name=["engulfing", "doji", "hammer", "morningstar"])
    
    last_row = patterns.iloc[-1]
    
    # Logic to pick the most relevant pattern from the last candle
    if last_row['CDL_ENGULFING'] != 0:
        res = "Bullish Engulfing" if last_row['CDL_ENGULFING'] > 0 else "Bearish Engulfing"
        return res, "The current candle body fully consumes the previous one, suggesting a strong trend reversal."
    if last_row['CDL_DOJI_10_0.1'] != 0:
        return "Doji", "Market indecision: the opening and closing prices are virtually equal."
    if last_row['CDL_HAMMER'] != 0:
        return "Hammer", "A bullish reversal pattern showing buyers pushed price back up after a drop."
    
    return "Neutral", "No major candlestick pattern identified in this timeframe."

def update_json():
    intervals = {
        "15m": Interval.in_15_minute,
        "30m": Interval.in_30_minute,
        "45m": Interval.in_45_minute,
        "1h": Interval.in_1_hour
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = {"timestamp": timestamp, "data": {}}

    for label, tv_interval in intervals.items():
        # Fetch enough bars for pattern recognition (min 30 suggested)
        df = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=tv_interval, n_bars=50)
        pattern, desc = analyze_patterns(df)
        
        new_entry["data"][label] = {
            "price": round(df['close'].iloc[-1], 2),
            "pattern": pattern,
            "explanation": desc
        }

    # Load and Append
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            full_history = json.load(f)
    else:
        full_history = []

    full_history.append(new_entry)
    
    # Save back to data/value.json
    with open(file_path, 'w') as f:
        json.dump(full_history, f, indent=4)

if __name__ == "__main__":
    update_json()
