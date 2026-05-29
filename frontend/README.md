# CryptoRadar — Real-Time Crypto Analytics Platform

A full-stack cryptocurrency analytics platform that tracks live prices in INR, predicts price trends using LSTM deep learning, analyzes market sentiment from news, and generates automated reports.

## 🔗 Live Demo
- **Frontend:** https://cryptoradar-qk2k.vercel.app
- **API:** https://cryptoradar-api.onrender.com/docs
- **Login:** admin / crypto2024

## 🚀 Features
- Live crypto prices in INR — BTC, ETH, BNB, SOL from CoinGecko API
- 90-day historical price data pipeline with SQLite storage
- Technical indicators — RSI, MACD, Bollinger Bands, Moving Averages
- LSTM deep learning model for 7-day Bitcoin price prediction
- News sentiment analysis using TextBlob and NewsAPI
- Auto-generated PDF market report with price table and charts
- React dashboard with dark blue theme — live clock, price cards, 4 charts
- REST API with JWT authentication — 8 endpoints

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Pipeline | Python, CoinGecko API, requests |
| Database | SQLite |
| Technical Analysis | pandas, numpy |
| Deep Learning | PyTorch, LSTM |
| Sentiment Analysis | TextBlob, NewsAPI |
| Backend API | FastAPI, JWT Auth |
| PDF Reports | reportlab, matplotlib |
| Frontend | React, Recharts |
| Deployment | Render (API), Vercel (Frontend) |

## 📊 Project Modules

### 1. Data Pipeline
- Fetch live crypto prices from CoinGecko API in INR
- Store 90-day historical data in SQLite
- Auto-update on every deployment

### 2. Technical Indicators
- RSI — overbought/oversold signals
- MACD — momentum and trend direction
- Bollinger Bands — volatility analysis
- Moving Averages — 7, 30, 90 day

### 3. LSTM Price Prediction
- PyTorch LSTM neural network
- Trained on 90-day Bitcoin price history
- 7-day forward price forecast
- Confidence intervals visualization

### 4. Sentiment Analysis
- Fetch latest crypto news from NewsAPI
- TextBlob sentiment scoring — positive, negative, neutral
- Correlation between news sentiment and price movement

### 5. FastAPI Backend
- 8 REST endpoints with JWT authentication
- Live prices, historical data, indicators, sentiment, forecast

### 6. React Dashboard
- Dark blue trading terminal theme
- Live price cards with 24H change
- 30-day price chart with coin selector
- Market sentiment bar chart
- Technical indicators panel
- LSTM 7-day forecast chart
- News feed with sentiment scores

### 7. PDF Report Generator
- Auto-generated market report
- Live price table, Bitcoin chart, sentiment analysis
- Auto-written market commentary

## 🏃 Run Locally

### Backend
```bash
pip install -r requirements.txt
python backend/data_pipeline/fetch_prices.py
python backend/sentiment/sentiment_analysis.py
python backend/ml_models/lstm_model.py
uvicorn backend.api.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure
cryptoradar/
├── backend/
│   ├── api/              # FastAPI endpoints
│   ├── data_pipeline/    # CoinGecko data fetching
│   ├── indicators/       # Technical indicators
│   ├── ml_models/        # LSTM price prediction
│   ├── sentiment/        # News sentiment analysis
│   └── reports/          # PDF report generator
├── frontend/
│   └── src/
│       └── components/   # React components
├── database/             # SQLite database
└── exports/              # Generated reports and data