import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
DATABASE_URL = 'database/cryptoradar.db'
COINS = ['bitcoin', 'ethereum', 'binancecoin', 'solana']
CURRENCY = 'inr'

COIN_SYMBOLS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'binancecoin': 'BNB',
    'solana': 'SOL',
    'ripple': 'XRP'
}

os.makedirs('database', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# ── Database Setup ─────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            symbol TEXT,
            name TEXT,
            price_inr REAL,
            market_cap_inr REAL,
            volume_24h_inr REAL,
            price_change_24h REAL,
            price_change_pct_24h REAL,
            high_24h REAL,
            low_24h REAL,
            circulating_supply REAL,
            timestamp TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            symbol TEXT,
            date TEXT,
            price_inr REAL,
            volume_inr REAL,
            market_cap_inr REAL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized.")

# ── Fetch Live Prices ──────────────────────────────────────────────────────────
def fetch_live_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': CURRENCY,
        'ids': ','.join(COINS),
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '24h'
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    records = []
    for coin in data:
        record = (
            coin['id'],
            coin['symbol'].upper(),
            coin['name'],
            coin['current_price'],
            coin['market_cap'],
            coin['total_volume'],
            coin.get('price_change_24h', 0),
            coin.get('price_change_percentage_24h', 0),
            coin.get('high_24h', 0),
            coin.get('low_24h', 0),
            coin.get('circulating_supply', 0),
            timestamp
        )
        records.append(record)

        print(f"{coin['symbol'].upper():>5} | ₹{coin['current_price']:>15,.2f} | "
              f"{coin.get('price_change_percentage_24h', 0):>+6.2f}%")

    cursor.executemany('''
        INSERT INTO prices (coin_id, symbol, name, price_inr, market_cap_inr,
        volume_24h_inr, price_change_24h, price_change_pct_24h, high_24h,
        low_24h, circulating_supply, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)

    conn.commit()
    conn.close()
    return pd.DataFrame(records, columns=[
        'coin_id', 'symbol', 'name', 'price_inr', 'market_cap_inr',
        'volume_24h_inr', 'price_change_24h', 'price_change_pct_24h',
        'high_24h', 'low_24h', 'circulating_supply', 'timestamp'
    ])

# ── Fetch Historical Prices ────────────────────────────────────────────────────
def fetch_historical(coin_id, days=90):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': CURRENCY, 'days': days, 'interval': 'daily'}

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    prices     = data['prices']
    volumes    = data['total_volumes']
    market_caps = data['market_caps']

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    symbol = COIN_SYMBOLS.get(coin_id, coin_id.upper())

    # Clear old historical data for this coin
    cursor.execute('DELETE FROM historical_prices WHERE coin_id = ?', (coin_id,))

    records = []
    for i in range(len(prices)):
        date = datetime.fromtimestamp(prices[i][0] / 1000).strftime('%Y-%m-%d')
        records.append((
            coin_id, symbol, date,
            prices[i][1], volumes[i][1], market_caps[i][1]
        ))

    cursor.executemany('''
        INSERT INTO historical_prices (coin_id, symbol, date, price_inr, volume_inr, market_cap_inr)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)

    conn.commit()
    conn.close()
    print(f"Historical data saved for {coin_id} — {len(records)} days")
    return pd.DataFrame(records, columns=['coin_id', 'symbol', 'date', 'price_inr', 'volume_inr', 'market_cap_inr'])

# ── Save to CSV ────────────────────────────────────────────────────────────────
def save_to_csv(df, filename):
    path = f'exports/{filename}'
    df.to_csv(path, index=False)
    print(f"Saved to {path}")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Initializing database...")
    init_db()

    print("\nFetching live prices...")
    live_df = fetch_live_prices()
    save_to_csv(live_df, 'live_prices.csv')

    print("\nFetching historical data (90 days)...")
    all_historical = []
    for coin in COINS:
        hist_df = fetch_historical(coin, days=90)
        all_historical.append(hist_df)

    combined = pd.concat(all_historical)
    save_to_csv(combined, 'historical_prices.csv')

    print(f"\nTotal historical records: {len(combined)}")
    print("\nPhase 1 complete.")