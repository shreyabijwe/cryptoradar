import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3
import os

DATABASE_URL = 'database/cryptoradar.db'
os.makedirs('exports/charts', exist_ok=True)

# ── Load Historical Data ───────────────────────────────────────────────────────
def load_historical(coin_id='bitcoin'):
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql(f"SELECT * FROM historical_prices WHERE coin_id='{coin_id}' ORDER BY date", conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df

# ── Moving Averages ────────────────────────────────────────────────────────────
def add_moving_averages(df):
    df['MA7']  = df['price_inr'].rolling(window=7).mean()
    df['MA30'] = df['price_inr'].rolling(window=30).mean()
    df['MA90'] = df['price_inr'].rolling(window=90).mean()
    return df

# ── RSI ────────────────────────────────────────────────────────────────────────
def calculate_rsi(df, period=14):
    delta  = df['price_inr'].diff()
    gain   = delta.where(delta > 0, 0)
    loss   = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi
    return df

# ── MACD ───────────────────────────────────────────────────────────────────────
def calculate_macd(df):
    ema12 = df['price_inr'].ewm(span=12, adjust=False).mean()
    ema26 = df['price_inr'].ewm(span=26, adjust=False).mean()
    df['MACD']        = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist']   = df['MACD'] - df['MACD_Signal']
    return df

# ── Bollinger Bands ────────────────────────────────────────────────────────────
def calculate_bollinger(df, window=20):
    df['BB_Mid']   = df['price_inr'].rolling(window=window).mean()
    df['BB_Upper'] = df['BB_Mid'] + 2 * df['price_inr'].rolling(window=window).std()
    df['BB_Lower'] = df['BB_Mid'] - 2 * df['price_inr'].rolling(window=window).std()
    return df

# ── Plot Price + Moving Averages ───────────────────────────────────────────────
def plot_price_ma(df, coin_id):
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['price_inr'], label='Price', color='#F18F01', linewidth=1.5)
    plt.plot(df.index, df['MA7'],  label='MA7',  color='#27ae60', linewidth=1, linestyle='--')
    plt.plot(df.index, df['MA30'], label='MA30', color='#2E86AB', linewidth=1, linestyle='--')
    plt.title(f'{coin_id.upper()} Price & Moving Averages (INR)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price (₹)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'exports/charts/{coin_id}_price_ma.png', dpi=150)
    plt.close()
    print(f"Price + MA chart saved for {coin_id}")

# ── Plot RSI ───────────────────────────────────────────────────────────────────
def plot_rsi(df, coin_id):
    plt.figure(figsize=(14, 4))
    plt.plot(df.index, df['RSI'], color='#8e44ad', linewidth=1.5)
    plt.axhline(70, color='red',   linestyle='--', alpha=0.7, label='Overbought (70)')
    plt.axhline(30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
    plt.fill_between(df.index, df['RSI'], 70, where=(df['RSI'] >= 70), alpha=0.2, color='red')
    plt.fill_between(df.index, df['RSI'], 30, where=(df['RSI'] <= 30), alpha=0.2, color='green')
    plt.title(f'{coin_id.upper()} RSI (14)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'exports/charts/{coin_id}_rsi.png', dpi=150)
    plt.close()
    print(f"RSI chart saved for {coin_id}")

# ── Plot MACD ──────────────────────────────────────────────────────────────────
def plot_macd(df, coin_id):
    plt.figure(figsize=(14, 5))
    plt.plot(df.index, df['MACD'],        label='MACD',   color='#2E86AB', linewidth=1.5)
    plt.plot(df.index, df['MACD_Signal'], label='Signal', color='#e74c3c', linewidth=1.5)
    plt.bar(df.index, df['MACD_Hist'],
            color=['#27ae60' if v >= 0 else '#e74c3c' for v in df['MACD_Hist']],
            alpha=0.4, label='Histogram')
    plt.axhline(0, color='white', linewidth=0.5)
    plt.title(f'{coin_id.upper()} MACD', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('MACD')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'exports/charts/{coin_id}_macd.png', dpi=150)
    plt.close()
    print(f"MACD chart saved for {coin_id}")

# ── Plot Bollinger Bands ───────────────────────────────────────────────────────
def plot_bollinger(df, coin_id):
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['price_inr'], label='Price',       color='#F18F01', linewidth=1.5)
    plt.plot(df.index, df['BB_Upper'],  label='Upper Band',  color='#e74c3c', linewidth=1, linestyle='--')
    plt.plot(df.index, df['BB_Mid'],    label='Middle Band', color='white',   linewidth=1, linestyle='--')
    plt.plot(df.index, df['BB_Lower'],  label='Lower Band',  color='#27ae60', linewidth=1, linestyle='--')
    plt.fill_between(df.index, df['BB_Upper'], df['BB_Lower'], alpha=0.1, color='#2E86AB')
    plt.title(f'{coin_id.upper()} Bollinger Bands (INR)', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price (₹)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'exports/charts/{coin_id}_bollinger.png', dpi=150)
    plt.close()
    print(f"Bollinger Bands chart saved for {coin_id}")

# ── Print Signal Summary ───────────────────────────────────────────────────────
def print_signals(df, coin_id):
    latest = df.iloc[-1]
    print(f"\n── {coin_id.upper()} Technical Signals ────────────────")
    print(f"  Price    : ₹{latest['price_inr']:,.2f}")
    print(f"  MA7      : ₹{latest['MA7']:,.2f}")
    print(f"  MA30     : ₹{latest['MA30']:,.2f}")
    print(f"  RSI      : {latest['RSI']:.2f} — ", end="")
    if latest['RSI'] > 70:
        print("OVERBOUGHT ⚠️")
    elif latest['RSI'] < 30:
        print("OVERSOLD 🟢")
    else:
        print("NEUTRAL")
    print(f"  MACD     : {latest['MACD']:.2f}")
    print(f"  Signal   : {latest['MACD_Signal']:.2f} — ", end="")
    if latest['MACD'] > latest['MACD_Signal']:
        print("BULLISH 📈")
    else:
        print("BEARISH 📉")
    print(f"  BB Upper : ₹{latest['BB_Upper']:,.2f}")
    print(f"  BB Lower : ₹{latest['BB_Lower']:,.2f}")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    coins = ['bitcoin', 'ethereum', 'binancecoin', 'solana']

    for coin in coins:
        print(f"\nProcessing {coin}...")
        df = load_historical(coin)
        df = add_moving_averages(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        df = calculate_bollinger(df)
        plot_price_ma(df, coin)
        plot_rsi(df, coin)
        plot_macd(df, coin)
        plot_bollinger(df, coin)
        print_signals(df, coin)

    print("\nPhase 2 complete.")