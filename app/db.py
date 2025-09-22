from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://Raj:912005@diabetes.kcgbgaq.mongodb.net/?retryWrites=true&w=majority&appName=diabetes"
)
DB_NAME = os.getenv("MONGO_DB", "diabetes_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
