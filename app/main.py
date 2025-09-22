from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, predict, datasets
from .db import db

app = FastAPI(title="Diabetes Prediction API 🚀")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])


# Root endpoint
@app.get("/")
async def root():
    # Try a simple DB query to ensure MongoDB is connected
    try:
        collections = await db.list_collection_names()
        return {
            "message": "Diabetes Prediction API is running with MongoDB 🚀",
            "db_status": "Connected",
            "collections": collections,
        }
    except Exception as e:
        return {
            "message": "Diabetes Prediction API is running 🚀",
            "db_status": f"Connection failed: {str(e)}",
        }
