"""Train and save a tiny SARIMAX model to backend/sarimax_model.pkl for local testing.
Run: python3 backend/train_dummy_sarimax.py
"""
import os
import argparse
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults
import warnings


def train_and_save(model_path: str = None):
    if model_path is None:
        # default to a file inside this backend directory
        model_path = os.path.join(os.path.dirname(__file__), "sarimax_model.pkl")

    MODEL_PATH = model_path

    # Create a simple time series with trend + seasonality
    np.random.seed(0)
    n = 120
    t = np.arange(n)
    seasonal = 2.0 * np.sin(2 * np.pi * t / 12)
    trend = 0.05 * t
    y = 10 + trend + seasonal + 0.5 * np.random.randn(n)

    # Put into pandas Series with a monthly index
    idx = pd.date_range(start="2000-01-01", periods=n, freq="M")
    series = pd.Series(y, index=idx)

    # Fit a small SARIMAX model
    # Use warnings.catch_warnings to surface convergence warnings but continue
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        model = SARIMAX(series, order=(1,1,1), seasonal_order=(1,0,1,12), enforce_stationarity=False, enforce_invertibility=False)
        results = model.fit(disp=False)

    # Ensure output directory exists
    out_dir = os.path.dirname(MODEL_PATH)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Save results
    results.save(MODEL_PATH)
    print(f"Saved SARIMAX model to {MODEL_PATH}")
    return MODEL_PATH


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train and save a tiny SARIMAX model for testing')
    parser.add_argument('--out', '-o', default=None, help='Path to save the SARIMAX model (default: backend/sarimax_model.pkl)')
    args = parser.parse_args()
    try:
        path = train_and_save(args.out)
    except Exception as e:
        print('Failed to train/save SARIMAX model:', e)
        raise
