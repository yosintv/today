import json
import os
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# Handle case-sensitivity in the tvDatafeed library
try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    from tvdatafeed import TvDatafeed, Interval

# 1. Setup Data Directory
folder_path = 'data'
file_path = os.path.join(folder_path, 'value.json')
os.makedirs(folder_path, exist_ok=True)

# 2. Initialize TradingView (Guest Mode)
tv = TvDatafeed()

def analyze_patterns(df):
    """Detects patterns and returns name + explanation"""
    # Standardize column names for pandas_ta (needs open, high, low, close)
    df.columns = [x.lower() for x in df.columns]
    
    # Calculate Candlestick Patterns
    # cdl_pattern returns a DataFrame where values are 100 (Bullish), -100 (Bearish), or 0
    patterns = df.ta.cdl_pattern(name=["engulfing", "doji", "hammer"])
    
    if patterns is None or patterns.empty:
        return "Normal", "Steady market movement with no specific candle formation."

    last_row = patterns.iloc[-1]
    
    # Pattern Logic
    if last_row.get('CDL_ENGULFING', 0) != 0:
        res = "Bullish Engulfing" if last_row['CDL_ENGULFING'] > 0 else "Bearish Engulfing"
        return res, "The current candle body fully consumes the previous one, suggesting a strong trend reversal."
    
    if last_row.get('CDL_DOJI_10_0.1', 0) != 0:
        return "Doji", "Indicates market indecision: the opening and closing prices are nearly equal."
    
    if last_row.get('CDL_HAMMER', 0) != 0:
        return "Hammer", "A bullish reversal pattern showing buyers pushed price back up after a drop."
    
    return "Normal", "No significant candlestick pattern identified in this timeframe."

def update_json():
    intervals = {
        "15m": Interval.in_15_minute,
        "30m": Interval.in_30_minute,
        "45m": Interval.in_45_minute,
        "1h": Interval.in_1_hour
    }
    
    # Current timestamp for recording
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M")
    new_entry = {"timestamp": timestamp_str, "data": {}}

    print(f"Fetching data for {timestamp_str}...")

    for label, tv_interval in intervals.items():
        try:
            # Fetch 50 bars to ensure enough data for pattern analysis
            df = tv.get_hist(symbol='XAUUSD', exchange='OANDA', interval=tv_interval, n_bars=50)
            
            if df is not None and not df.empty:
                pattern, desc = analyze_patterns(df)
                new_entry["data"][label] = {
                    "price": round(df['close'].iloc[-1], 2),
                    "pattern": pattern,
                    "explanation": desc
                }
            else:
                print(f"Warning: No data returned for {label}")
        except Exception as e:
            print(f"Error fetching {label}: {e}")

    # 3. Load, Append, and Save
    full_history = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                full_history = json.load(f)
            except json.JSONDecodeError:
                full_history = []

    # Check for duplicate timestamp to prevent double-entries
    if not any(d.get('timestamp') == timestamp_str for d in full_history):
        full_history.append(new_entry)
        
        # Keep only last 1000 records to keep file size small
        if len(full_history) > 1000:
            full_history = full_history[-1000:]

        with open(file_path, 'w') as f:
            json.dump(full_history, f, indent=4)
        print("Successfully updated data/value.json")
    else:
        print("Data for this timestamp already exists. Skipping.")

if __name__ == "__main__":
    update_json()
