# app.py
# Minimal API so FE can call with input text and get "compliant"/"violated".
# Run with: uvicorn app:app --reload

# backend/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
import os
from typing import List, Optional

MODEL_PATH = "sarimax_model.pkl"

# Load model lazily; don't crash at import time if file is missing.
model: Optional[SARIMAXResults] = None
if os.path.exists(MODEL_PATH):
    try:
        model = SARIMAXResults.load(MODEL_PATH)
    except Exception as e:
        # keep model as None; endpoint will return a clear 503 with this info
        print(f"Warning: failed to load model from {MODEL_PATH}: {e}")

app = FastAPI(title="Take a seat — SARIMAX Forecast API")

class ForecastRequest(BaseModel):
    steps: int

class ForecastResponse(BaseModel):
    forecast: List[float]

@app.post("/forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{MODEL_PATH} not found or failed to load. Train and save a SARIMAX model first: "
                "use `results.save('sarimax_model.pkl')` when training."
            ),
        )
    pred = model.get_forecast(steps=req.steps)
    mean = pred.predicted_mean
    return ForecastResponse(forecast=[float(x) for x in mean])