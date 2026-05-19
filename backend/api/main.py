from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import sqlite3
import os
import torch
import joblib
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CryptoRadar — Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("JWT_SECRET", "cryptoradar_secret_key_shreya_2024")
ALGORITHM  = "HS256"
security   = HTTPBearer()
DATABASE_URL = 'database/cryptoradar.db'

def create_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db():
    return sqlite3.connect(DATABASE_URL)

class LoginRequest(BaseModel):
    username: str
    password: str

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "CryptoRadar Analytics API", "status": "running"}

@app.post("/login")
def login(req: LoginRequest):
    if req.username == "admin" and req.password == "crypto2024":
        token = create_token(req.username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/prices")
def get_prices(user=Depends(verify_token)):
    conn = get_db()
    df = pd.read_sql("""
        SELECT coin_id, symbol, name, price_inr, market_cap_inr,
               volume_24h_inr, price_change_pct_24h, high_24h, low_24h, timestamp
        FROM prices
        WHERE timestamp = (SELECT MAX(timestamp) FROM prices)
    """, conn)
    conn.close()
    return df.to_dict(orient='records')

@app.get("/historical/{coin_id}")
def get_historical(coin_id: str, days: int = 30, user=Depends(verify_token)):
    conn = get_db()
    df = pd.read_sql(f"""
        SELECT date, price_inr, volume_inr, market_cap_inr
        FROM historical_prices
        WHERE coin_id='{coin_id}'
        ORDER BY date DESC
        LIMIT {days}
    """, conn)
    conn.close()
    df = df.sort_values('date')
    return df.to_dict(orient='records')

@app.get("/indicators/{coin_id}")
def get_indicators(coin_id: str, user=Depends(verify_token)):
    conn = get_db()
    df = pd.read_sql(f"""
        SELECT date, price_inr FROM historical_prices
        WHERE coin_id='{coin_id}' ORDER BY date
    """, conn)
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail="Coin not found")

    # Calculate indicators
    df['MA7']  = df['price_inr'].rolling(7).mean()
    df['MA30'] = df['price_inr'].rolling(30).mean()

    delta = df['price_inr'].diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs    = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    ema12 = df['price_inr'].ewm(span=12).mean()
    ema26 = df['price_inr'].ewm(span=26).mean()
    df['MACD']        = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

    df['BB_Mid']   = df['price_inr'].rolling(20).mean()
    df['BB_Upper'] = df['BB_Mid'] + 2 * df['price_inr'].rolling(20).std()
    df['BB_Lower'] = df['BB_Mid'] - 2 * df['price_inr'].rolling(20).std()

    latest = df.iloc[-1]
    return {
        "coin_id": coin_id,
        "price_inr": latest['price_inr'],
        "MA7": round(latest['MA7'], 2),
        "MA30": round(latest['MA30'], 2),
        "RSI": round(latest['RSI'], 2),
        "MACD": round(latest['MACD'], 2),
        "MACD_Signal": round(latest['MACD_Signal'], 2),
        "BB_Upper": round(latest['BB_Upper'], 2),
        "BB_Lower": round(latest['BB_Lower'], 2),
        "signal": "BULLISH" if latest['MACD'] > latest['MACD_Signal'] else "BEARISH"
    }

@app.get("/sentiment")
def get_sentiment(user=Depends(verify_token)):
    conn = get_db()
    df = pd.read_sql("SELECT * FROM sentiment", conn)
    conn.close()

    if df.empty:
        return []

    summary = df.groupby('coin_id').agg(
        total=('id', 'count'),
        positive=('sentiment_label', lambda x: (x == 'Positive').sum()),
        negative=('sentiment_label', lambda x: (x == 'Negative').sum()),
        neutral=('sentiment_label', lambda x: (x == 'Neutral').sum()),
        avg_polarity=('polarity', 'mean')
    ).reset_index().round(3)

    summary['overall'] = summary['avg_polarity'].apply(
        lambda x: 'BULLISH' if x > 0.1 else 'BEARISH' if x < -0.1 else 'NEUTRAL'
    )
    return summary.to_dict(orient='records')

@app.get("/news/{coin_id}")
def get_news(coin_id: str, user=Depends(verify_token)):
    conn = get_db()
    df = pd.read_sql(f"""
        SELECT headline, source, published_at, polarity, sentiment_label
        FROM sentiment WHERE coin_id='{coin_id}'
        ORDER BY published_at DESC LIMIT 10
    """, conn)
    conn.close()
    return df.to_dict(orient='records')

@app.get("/forecast/{coin_id}")
def get_forecast(coin_id: str, user=Depends(verify_token)):
    try:
        from backend.ml_models.lstm_model import (
            LSTMModel, load_data, prepare_sequences, forecast_next_7_days
        )
        from sklearn.preprocessing import MinMaxScaler
        import numpy as np

        model_path  = f'backend/ml_models/saved/{coin_id}_lstm.pth'
        scaler_path = f'backend/ml_models/saved/{coin_id}_scaler.pkl'

        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail=f"No model found for {coin_id}")

        df     = load_data(coin_id)
        prices = df['price_inr'].values
        scaler = joblib.load(scaler_path)

        scaled = scaler.transform(prices.reshape(-1, 1))

        model = LSTMModel()
        model.load_state_dict(torch.load(model_path, weights_only=True))
        model.eval()

        forecasts = forecast_next_7_days(model, scaled, scaler)

        return {
            "coin_id": coin_id,
            "forecast_inr": [round(float(f), 2) for f in forecasts],
            "days": list(range(1, 8))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis")
def get_kpis(user=Depends(verify_token)):
    conn = get_db()
    prices_df = pd.read_sql("""
        SELECT coin_id, symbol, price_inr, price_change_pct_24h, market_cap_inr
        FROM prices
        WHERE timestamp = (SELECT MAX(timestamp) FROM prices)
    """, conn)
    sentiment_df = pd.read_sql("SELECT coin_id, polarity FROM sentiment", conn)
    conn.close()

    total_market_cap = prices_df['market_cap_inr'].sum()
    best_performer   = prices_df.loc[prices_df['price_change_pct_24h'].idxmax(), 'symbol']
    worst_performer  = prices_df.loc[prices_df['price_change_pct_24h'].idxmin(), 'symbol']
    avg_sentiment    = round(sentiment_df['polarity'].mean(), 3)

    return {
        "total_market_cap_inr": round(total_market_cap, 2),
        "best_performer_24h": best_performer,
        "worst_performer_24h": worst_performer,
        "avg_market_sentiment": avg_sentiment,
        "coins_tracked": len(prices_df),
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }