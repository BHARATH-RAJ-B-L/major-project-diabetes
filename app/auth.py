# backend/app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from app.db import db
from app.schemas import UserCreate, UserOut, Token

SECRET_KEY = "change_this_secret_in_prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# -------------------------------
# Helper Functions
# -------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_db():
    return db

# -------------------------------
# CRUD Helpers
# -------------------------------
async def get_user_by_username(db, username: str):
    return await db["users"].find_one({"username": username})

async def get_user_by_email(db, email: str):
    return await db["users"].find_one({"email": email})

# -------------------------------
# Dependency
# -------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# -------------------------------
# Routes
# -------------------------------
@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db=Depends(get_db)):
    if await get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user_dict = user.dict()
    user_dict["password"] = bcrypt.hash(user_dict["password"])
    result = await db["users"].insert_one(user_dict)
    return {**user_dict, "_id": result.inserted_id}


@router.post("/login", response_model=Token)
async def login_user(user: UserCreate, db=Depends(get_db)):
    db_user = await get_user_by_username(db, user.username)
    if not db_user or not bcrypt.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
