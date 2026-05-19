import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3
import os
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import warnings
warnings.filterwarnings('ignore')

DATABASE_URL = 'database/cryptoradar.db'
os.makedirs('exports/charts', exist_ok=True)
os.makedirs('backend/ml_models/saved', exist_ok=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
def load_data(coin_id='bitcoin'):
    conn = sqlite3.connect(DATABASE_URL)
    df = pd.read_sql(
        f"SELECT date, price_inr FROM historical_prices WHERE coin_id='{coin_id}' ORDER BY date",
        conn
    )
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

# ── Prepare Sequences ──────────────────────────────────────────────────────────
def prepare_sequences(prices, seq_length=30):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(prices.reshape(-1, 1))

    X, y = [], []
    for i in range(seq_length, len(scaled)):
        X.append(scaled[i - seq_length:i, 0])
        y.append(scaled[i, 0])

    X = np.array(X)
    y = np.array(y)

    # Train/test split
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Convert to tensors
    X_train = torch.FloatTensor(X_train).unsqueeze(-1)
    X_test  = torch.FloatTensor(X_test).unsqueeze(-1)
    y_train = torch.FloatTensor(y_train)
    y_test  = torch.FloatTensor(y_test)

    return X_train, X_test, y_train, y_test, scaler, scaled

# ── LSTM Model ─────────────────────────────────────────────────────────────────
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers  = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc   = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out.squeeze()

# ── Train Model ────────────────────────────────────────────────────────────────
def train_model(X_train, y_train, epochs=50):
    model     = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    print("Training LSTM model...")
    losses = []
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss   = criterion(output, y_train)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/{epochs} — Loss: {loss.item():.6f}")

    return model, losses

# ── Evaluate ───────────────────────────────────────────────────────────────────
def evaluate_model(model, X_test, y_test, scaler):
    model.eval()
    with torch.no_grad():
        predictions = model(X_test).numpy()

    y_test_np = y_test.numpy()

    # Inverse transform
    predictions_inr = scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
    actual_inr      = scaler.inverse_transform(y_test_np.reshape(-1, 1)).flatten()

    mae  = mean_absolute_error(actual_inr, predictions_inr)
    rmse = np.sqrt(mean_squared_error(actual_inr, predictions_inr))

    print(f"\nModel Evaluation:")
    print(f"  MAE  : ₹{mae:,.2f}")
    print(f"  RMSE : ₹{rmse:,.2f}")

    return predictions_inr, actual_inr

# ── Forecast Next 7 Days ───────────────────────────────────────────────────────
def forecast_next_7_days(model, scaled, scaler, seq_length=30):
    model.eval()
    last_sequence = scaled[-seq_length:].flatten()
    forecasts = []

    for _ in range(7):
        seq_tensor = torch.FloatTensor(last_sequence).unsqueeze(0).unsqueeze(-1)
        with torch.no_grad():
            pred = model(seq_tensor).item()
        forecasts.append(pred)
        last_sequence = np.append(last_sequence[1:], pred)

    forecasts_inr = scaler.inverse_transform(np.array(forecasts).reshape(-1, 1)).flatten()
    return forecasts_inr

# ── Plot Predictions ───────────────────────────────────────────────────────────
def plot_predictions(actual, predictions, forecasts, coin_id, df):
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Actual vs Predicted
    axes[0].plot(actual,      label='Actual Price',    color='#F18F01', linewidth=2)
    axes[0].plot(predictions, label='Predicted Price', color='#2E86AB', linewidth=2, linestyle='--')
    axes[0].set_title(f'{coin_id.upper()} — LSTM Price Prediction (INR)', fontsize=13, fontweight='bold')
    axes[0].set_ylabel('Price (₹)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 7-day forecast
    last_price = actual[-1]
    forecast_x = range(len(actual), len(actual) + 7)
    axes[1].plot(list(range(len(actual))), actual, color='#F18F01', linewidth=2, label='Historical')
    axes[1].plot(list(forecast_x), forecasts, color='#27ae60', linewidth=2,
                 linestyle='--', marker='o', label='7-Day Forecast')
    axes[1].fill_between(list(forecast_x),
                         forecasts * 0.95, forecasts * 1.05,
                         alpha=0.2, color='#27ae60', label='Confidence Band')
    axes[1].set_title(f'{coin_id.upper()} — 7-Day Price Forecast (INR)', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('Price (₹)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'exports/charts/{coin_id}_lstm_prediction.png', dpi=150)
    plt.close()
    print(f"LSTM prediction chart saved for {coin_id}")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    coin_id = 'bitcoin'
    seq_length = 30

    print(f"Loading {coin_id} data...")
    df = load_data(coin_id)
    prices = df['price_inr'].values

    print("Preparing sequences...")
    X_train, X_test, y_train, y_test, scaler, scaled = prepare_sequences(prices, seq_length)
    print(f"Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    model, losses = train_model(X_train, y_train, epochs=50)

    predictions_inr, actual_inr = evaluate_model(model, X_test, y_test, scaler)

    print("\nForecasting next 7 days...")
    forecasts = forecast_next_7_days(model, scaled, scaler, seq_length)

    print("\n7-Day Bitcoin Price Forecast (INR):")
    for i, price in enumerate(forecasts, 1):
        print(f"  Day {i}: ₹{price:,.2f}")

    plot_predictions(actual_inr, predictions_inr, forecasts, coin_id, df)

    # Save model
    torch.save(model.state_dict(), f'backend/ml_models/saved/{coin_id}_lstm.pth')
    joblib.dump(scaler, f'backend/ml_models/saved/{coin_id}_scaler.pkl')
    print(f"\nModel saved.")
    print("\nPhase 3 complete.")