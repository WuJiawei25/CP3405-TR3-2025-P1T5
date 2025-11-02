# app.py
# Minimal API so FE can call with input text and get "compliant"/"violated".
# Run with: uvicorn app:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os

MODEL_PATH = "seat_policy_model.joblib"

# Load the trained pipeline (TF-IDF + LogisticRegression)
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"{MODEL_PATH} not found. Train first: `python train_model.py`"
    )
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Take a seat — Text Policy Checker")

class CheckRequest(BaseModel):
    text: str

class CheckResponse(BaseModel):
    label: str
    probability: float  # probability for the predicted label (0..1)

@app.post("/check", response_model=CheckResponse)
def check_text(req: CheckRequest):
    # Predict class and probability
    proba = model.predict_proba([req.text])[0]  # [p_compliant, p_violated] (ordered by model.classes_)
    classes = model.classes_.tolist()
    idx = int(proba.argmax())
    label = classes[idx]
    return CheckResponse(label=label, probability=float(proba[idx]))
