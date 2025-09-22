# backend/app/routes/predict.py
from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..predict_utils import preprocess_and_predict
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/predict", tags=["predict"])


class PredictRequest(BaseModel):
    dataset: str  # 'sylhet' or 'pima'
    model: str  # 'dbn' or 'attn_dbn' (prefix)
    features: Dict[str, Any]


@router.post("/", dependencies=[Depends(get_current_user)])
def predict(req: PredictRequest):
    try:
        out = preprocess_and_predict(req.dataset, req.model, req.features)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return out
