# backend/app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId
from .db import PyObjectId

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
