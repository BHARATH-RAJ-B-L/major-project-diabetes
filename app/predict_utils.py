# backend/app/predict_utils.py
import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]  # backend/app/..
PIPELINE_DIR = BASE / "pipelines"
MODEL_DIR = BASE / "models"
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

# Load feature orders at startup
def load_feature_orders():
    orders = {}
    sylhet_path = PROCESSED_DIR / "sylhet_clean.csv"
    pima_path = PROCESSED_DIR / "pima_clean.csv"
    if sylhet_path.exists():
        syl = pd.read_csv(sylhet_path)
        orders["sylhet"] = [c for c in syl.columns if c != "class"]
    if pima_path.exists():
        pima = pd.read_csv(pima_path)
        orders["pima"] = [c for c in pima.columns if c != "Outcome"]
    return orders

FEATURE_ORDERS = load_feature_orders()

def preprocess_and_predict(dataset: str, model_name: str, input_dict: dict):
    """
    dataset: 'sylhet' or 'pima'
    model_name: 'dbn' or 'attn_dbn' (string prefix)
    input_dict: mapping feature->value (raw values)
    """
    dataset = dataset.lower()
    if dataset not in FEATURE_ORDERS:
        raise ValueError("Unknown dataset")

    feature_order = FEATURE_ORDERS[dataset]
    # Build row list in order
    row = []
    for col in feature_order:
        if col == "age" and dataset == "sylhet":
            # Accept raw age in years
            raw_age = input_dict.get("age", None)
            if raw_age is None:
                raise ValueError("age required")
            # apply sylhet scaler
            scaler = joblib.load(PIPELINE_DIR / "sylhet_age_scaler.joblib")
            scaled = scaler.transform([[float(raw_age)]])[0][0]
            row.append(scaled)
        else:
            val = input_dict.get(col)
            # try to normalize Yes/No or Male/Female
            if isinstance(val, str):
                s = val.strip().lower()
                if s in ("yes", "y", "1", "true", "t"):
                    row.append(1)
                elif s in ("no", "n", "0", "false", "f"):
                    row.append(0)
                elif s in ("male",):
                    row.append(1)
                elif s in ("female",):
                    row.append(0)
                else:
                    try:
                        row.append(float(val))
                    except:
                        raise ValueError(f"Cannot parse feature {col} value {val}")
            elif val is None:
                # if missing - put NaN (pima pipeline will impute)
                row.append(np.nan)
            else:
                row.append(val)
    X = np.array(row).reshape(1, -1)

    # If pima, apply pima pipeline
    if dataset == "pima":
        pipeline = joblib.load(PIPELINE_DIR / "pima_pipeline.joblib")
        X = pipeline.transform(X)

    # Load model
    model_file = f"{model_name}_{dataset}.h5"  # e.g. dbn_sylhet.h5
    model_path = MODEL_DIR / model_file
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    import tensorflow as tf
    model = tf.keras.models.load_model(str(model_path))
    proba = float(model.predict(X)[0][0])
    return {"probability": proba, "predicted_class": int(proba > 0.5)}
