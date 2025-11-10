import os
import json
import argparse
import warnings
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults

def _safe_base_dir() -> str:
    """Return a base directory robust to Jupyter/REPL where __file__ may be missing."""
    return os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()


def _ensure_dir(path: str) -> None:
    """Ensure the directory for a file path exists."""
    out_dir = os.path.dirname(path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)


def _parse_tuple_ints(csv_like: str, expected_len: int) -> Tuple[int, ...]:
    """Parse '1,0,1' or '1,0,1,12' -> tuple of ints with length check."""
    parts = [int(x.strip()) for x in csv_like.split(",")]
    if len(parts) != expected_len:
        raise ValueError(f"Expected {expected_len} integers, got {len(parts)} from '{csv_like}'")
    return tuple(parts)


def _infer_datetime_col(df: pd.DataFrame, override: Optional[str]) -> str:
    """Try to find the datetime column name for exog CSV."""
    if override:
        if override not in df.columns:
            raise ValueError(f"Date column '{override}' not found in exog CSV. Available: {list(df.columns)}")
        return override
    for cand in ("date", "ds", "timestamp", "time", "Date", "DATE"):
        if cand in df.columns:
            return cand
    # fallback: first column
    return df.columns[0]


def _read_exog_csv(path: str, freq: str, idx_like: pd.DatetimeIndex, date_col: Optional[str] = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    dcol = _infer_datetime_col(df, date_col)
    df[dcol] = pd.to_datetime(df[dcol])
    df = df.set_index(dcol).sort_index()

    # If index freq is missing, try to conform to requested freq
    # We require that final exog has rows exactly at idx_like
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)

    # If the CSV has higher frequency than target, try to aggregate by period-end/start.
    # Here we choose 'last' to keep it simple; adjust if needed.
    if freq in ("M", "MS"):
        rule = "M" if freq == "M" else "MS"
        # If the existing index is not already on requested freq anchors, resample:
        if pd.infer_freq(df.index) != rule:
            df = df.resample(rule).last()

    # Align strictly to training index
    try:
        exog = df.loc[idx_like]
    except KeyError:
        # Try to intersect if exact alignment fails
        exog = df.reindex(idx_like)

    if exog.isnull().any().any():
        missing = int(exog.isnull().any(axis=1).sum())
        raise ValueError(
            f"Exogenous CSV cannot be aligned to training index: {missing} rows with NaNs. "
            f"Ensure dates cover exactly {idx_like[0]} to {idx_like[-1]} with freq={freq}."
        )
    return exog

# Portable save / load

def portable_save(series: pd.Series, results: SARIMAXResults, portable_json_path: str) -> None:
    """
    Save a portable bundle (JSON + NPZ) that allows reconstructing a SARIMAXResults
    without relying on pickle or exact statsmodels/python versions.

    JSON contains: order, seasonal_order, flags, freq, start, nobs, params
    NPZ contains:  y (the training endog values)
    """
    meta = {
        "order": list(results.model.order),
        "seasonal_order": list(results.model.seasonal_order),
        "enforce_stationarity": bool(results.model.enforce_stationarity),
        "enforce_invertibility": bool(results.model.enforce_invertibility),
        "freq": (series.index.freqstr or pd.infer_freq(series.index)),
        "start": series.index[0].isoformat(),
        "nobs": int(series.shape[0]),
        "params": results.params.tolist(),
    }

    _ensure_dir(portable_json_path)
    base, _ = os.path.splitext(portable_json_path)
    npz_path = base + ".npz"

    with open(portable_json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    np.savez(npz_path, y=series.values)


def portable_load(portable_json_path: str) -> SARIMAXResults:
    """
    Reconstruct a SARIMAXResults object from a portable bundle (JSON + NPZ).
    We rebuild the model on the original endog and apply the saved params via model.filter(...).
    """
    with open(portable_json_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    base, _ = os.path.splitext(portable_json_path)
    npz_path = base + ".npz"
    arr = np.load(npz_path)
    y = arr["y"]

    idx = pd.date_range(
        start=pd.to_datetime(meta["start"]),
        periods=meta["nobs"],
        freq=meta["freq"]
    )
    series = pd.Series(y, index=idx)

    model = SARIMAX(
        series,
        order=tuple(meta["order"]),
        seasonal_order=tuple(meta["seasonal_order"]),
        enforce_stationarity=meta["enforce_stationarity"],
        enforce_invertibility=meta["enforce_invertibility"],
    )
    # Use filter with fixed params to avoid re-optimization
    res = model.filter(np.asarray(meta["params"]))
    return res

# Core training

def train_and_save(
    model_path: Optional[str] = None,
    *,
    freq: str = "M",
    order: Tuple[int, int, int] = (1, 1, 1),
    seasonal_order: Tuple[int, int, int, int] = (1, 0, 1, 12),
    show_warnings: bool = True,
    exog_csv: Optional[str] = None,
    exog_date_col: Optional[str] = None,
    random_seed: int = 0,
    n: int = 120,
    forecast_steps: int = 0,
) -> str:

    # Resolve output path robustly to Jupyter/REPL
    if model_path is None:
        base_dir = _safe_base_dir()
        model_path = os.path.join(base_dir, "sarimax_model.pkl")

    # Simulate seasonal + trend series
    np.random.seed(random_seed)
    t = np.arange(n)
    m = seasonal_order[3]  # seasonal period m from seasonal_order
    seasonal = 2.0 * np.sin(2 * np.pi * t / m)
    trend = 0.05 * t
    y = 10 + trend + seasonal + 0.5 * np.random.randn(n)

    # Monthly index: month-end 'M' or month-start 'MS'
    idx = pd.date_range(start="2025-01-01", periods=n, freq=freq)
    series = pd.Series(y, index=idx)

    # Optional exogenous regressors
    exog = None
    if exog_csv:
        exog = _read_exog_csv(exog_csv, freq=freq, idx_like=series.index, date_col=exog_date_col)
        if len(exog) != len(series):
            raise ValueError(f"exog length {len(exog)} != series length {len(series)} after alignment")

    # Fit SARIMAX
    with warnings.catch_warnings():
        # show warnings by default (so you can see convergence issues)
        warnings.simplefilter('default' if show_warnings else 'ignore')
        model = SARIMAX(
            series,
            exog=exog,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        results = model.fit(disp=False)

    # Save results (pickle + portable)
    _ensure_dir(model_path)
    results.save(model_path)

    # portable bundle lives alongside .pkl, e.g. sarimax_model.portable.json + .npz
    base, _ = os.path.splitext(model_path)
    portable_json_path = base + ".portable.json"
    portable_save(series, results, portable_json_path)

    print(f"[OK] Pickle saved to: {model_path}")
    print(f"[OK] Portable bundle saved to: {portable_json_path} (+ .npz)")

    # Optional forecast demo
    if forecast_steps and forecast_steps > 0:
        pred = results.get_forecast(steps=forecast_steps)
        mean = pred.predicted_mean
        ci = pred.conf_int()
        print("\n=== Forecast (head) ===")
        print(mean.head())
        print("\n=== 95% CI (head) ===")
        print(ci.head())

    return model_path


def main():
    parser = argparse.ArgumentParser(
        description="Train and save a tiny SARIMAX model (pickle + portable), with options for freq/order/seasonal_order/exog."
    )
    parser.add_argument('--out', '-o', default=None,
                        help='Path to save the SARIMAX pickle model (default: <this_dir>/sarimax_model.pkl)')
    parser.add_argument('--freq', default="M", choices=["M", "MS"],
                        help='Pandas frequency for monthly data: "M"=month-end, "MS"=month-start (default: M)')
    parser.add_argument('--order', default="1,1,1",
                        help='ARIMA (p,d,q) as CSV string, e.g. "1,1,1"')
    parser.add_argument('--seasonal-order', default="1,0,1,12",
                        help='Seasonal (P,D,Q,m) as CSV string, e.g. "1,0,1,12"')
    parser.add_argument('--suppress-warnings', action='store_true',
                        help='Hide convergence/parameter warnings during fit (default: show)')
    parser.add_argument('--exog-csv', default=None,
                        help='Path to CSV containing exogenous regressors with a date column')
    parser.add_argument('--exog-date-col', default=None,
                        help='Name of the date column in exog CSV (auto-detect if omitted)')
    parser.add_argument('--seed', type=int, default=0, help='Random seed for synthetic data (default: 0)')
    parser.add_argument('--n', type=int, default=120, help='Number of periods to simulate (default: 120)')
    parser.add_argument('--forecast', type=int, default=0, help='Immediately forecast N steps after training (default: 0)')

    args = parser.parse_args()

    try:
        order = _parse_tuple_ints(args.order, 3)
        seasonal_order = _parse_tuple_ints(args.seasonal_order, 4)
        train_and_save(
            args.out,
            freq=args.freq,
            order=order,
            seasonal_order=seasonal_order,
            show_warnings=not args.suppress_warnings,
            exog_csv=args.exog_csv,
            exog_date_col=args.exog_date_col,
            random_seed=args.seed,
            n=args.n,
            forecast_steps=args.forecast,
        )
    except Exception as e:
        print('Failed to train/save SARIMAX model:', e)
        raise


if __name__ == '__main__':
    main()
