import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from textblob import TextBlob
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY  = os.getenv('NEWS_API_KEY')
DATABASE_URL  = 'database/cryptoradar.db'
os.makedirs('exports/charts', exist_ok=True)

COINS = {
    'bitcoin':     ['bitcoin', 'BTC'],
    'ethereum':    ['ethereum', 'ETH'],
    'binancecoin': ['binance', 'BNB'],
    'solana':      ['solana', 'SOL'],
}

# ── Init DB Table ──────────────────────────────────────────────────────────────
def init_sentiment_table():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            headline TEXT,
            source TEXT,
            published_at TEXT,
            polarity REAL,
            subjectivity REAL,
            sentiment_label TEXT,
            fetched_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ── Fetch News ─────────────────────────────────────────────────────────────────
def fetch_news(coin_id, keywords):
    url = "https://newsapi.org/v2/everything"
    query = ' OR '.join(keywords)
    params = {
        'q': query,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 20,
        'apiKey': NEWS_API_KEY
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if data.get('status') != 'ok':
        print(f"  API error for {coin_id}: {data.get('message', 'Unknown error')}")
        return []

    articles = data.get('articles', [])
    print(f"  Fetched {len(articles)} articles for {coin_id}")
    return articles

# ── Analyze Sentiment ──────────────────────────────────────────────────────────
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity     = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.1:
        label = 'Positive'
    elif polarity < -0.1:
        label = 'Negative'
    else:
        label = 'Neutral'

    return polarity, subjectivity, label

# ── Process & Save ─────────────────────────────────────────────────────────────
def process_news(coin_id, articles):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sentiment WHERE coin_id = ?', (coin_id,))

    records = []
    fetched_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for article in articles:
        headline = article.get('title', '')
        if not headline or headline == '[Removed]':
            continue

        source       = article.get('source', {}).get('name', '')
        published_at = article.get('publishedAt', '')

        polarity, subjectivity, label = analyze_sentiment(headline)

        records.append((
            coin_id, headline, source, published_at,
            polarity, subjectivity, label, fetched_at
        ))

    cursor.executemany('''
        INSERT INTO sentiment (coin_id, headline, source, published_at,
        polarity, subjectivity, sentiment_label, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)

    conn.commit()
    conn.close()
    return records

# ── Sentiment Summary ──────────────────────────────────────────────────────────
def sentiment_summary(coin_id):
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql(f"SELECT * FROM sentiment WHERE coin_id='{coin_id}'", conn)
    conn.close()

    if df.empty:
        return None

    total     = len(df)
    positive  = len(df[df['sentiment_label'] == 'Positive'])
    negative  = len(df[df['sentiment_label'] == 'Negative'])
    neutral   = len(df[df['sentiment_label'] == 'Neutral'])
    avg_pol   = df['polarity'].mean()

    if avg_pol > 0.1:
        overall = 'BULLISH 📈'
    elif avg_pol < -0.1:
        overall = 'BEARISH 📉'
    else:
        overall = 'NEUTRAL ➡️'

    print(f"\n── {coin_id.upper()} Sentiment Summary ────────────────")
    print(f"  Total Articles : {total}")
    print(f"  Positive       : {positive} ({positive/total*100:.1f}%)")
    print(f"  Negative       : {negative} ({negative/total*100:.1f}%)")
    print(f"  Neutral        : {neutral} ({neutral/total*100:.1f}%)")
    print(f"  Avg Polarity   : {avg_pol:.3f}")
    print(f"  Overall Signal : {overall}")

    return {
        'coin_id': coin_id,
        'total': total,
        'positive': positive,
        'negative': negative,
        'neutral': neutral,
        'avg_polarity': round(avg_pol, 3),
        'overall': overall
    }

# ── Plot Sentiment ─────────────────────────────────────────────────────────────
def plot_sentiment(summaries):
    coins   = [s['coin_id'].upper() for s in summaries]
    pos     = [s['positive']  for s in summaries]
    neg     = [s['negative']  for s in summaries]
    neu     = [s['neutral']   for s in summaries]
    pol     = [s['avg_polarity'] for s in summaries]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Stacked bar
    x = range(len(coins))
    axes[0].bar(x, pos, label='Positive', color='#27ae60')
    axes[0].bar(x, neu, bottom=pos, label='Neutral', color='#F18F01')
    axes[0].bar(x, neg, bottom=[p+n for p, n in zip(pos, neu)], label='Negative', color='#e74c3c')
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(coins)
    axes[0].set_title('Sentiment Distribution by Coin')
    axes[0].set_ylabel('Number of Articles')
    axes[0].legend()

    # Polarity bar
    colors = ['#27ae60' if p > 0 else '#e74c3c' for p in pol]
    axes[1].bar(coins, pol, color=colors)
    axes[1].axhline(0, color='white', linewidth=0.5)
    axes[1].set_title('Average Sentiment Polarity by Coin')
    axes[1].set_ylabel('Polarity Score')

    plt.tight_layout()
    plt.savefig('exports/charts/sentiment_analysis.png', dpi=150)
    plt.close()
    print("\nSentiment chart saved.")

# ── Save to CSV ────────────────────────────────────────────────────────────────
def save_sentiment_csv():
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM sentiment", conn)
    conn.close()
    df.to_csv('exports/sentiment_data.csv', index=False)
    print("Sentiment data saved to exports/sentiment_data.csv")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_sentiment_table()
    summaries = []

    for coin_id, keywords in COINS.items():
        print(f"\nFetching news for {coin_id}...")
        articles = fetch_news(coin_id, keywords)
        if articles:
            process_news(coin_id, articles)
            summary = sentiment_summary(coin_id)
            if summary:
                summaries.append(summary)

    if summaries:
        plot_sentiment(summaries)
        save_sentiment_csv()

    print("\nPhase 4 complete.")