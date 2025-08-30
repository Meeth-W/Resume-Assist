from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from pymongo import MongoClient
from bson import ObjectId
import os
import jwt

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Auth"])

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB", "resume_assist")
USERS_COLL = "users"

SECRET_KEY = os.getenv("JWT_SECRET", "temp-secret-i-will-change-one-day")
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_MIN", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=15)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserPublic(BaseModel):
    id: str
    username: str
    name: str
    email: EmailStr
    phone_number: str
    created_at: datetime

class UpdateAccountRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------\

ph = PasswordHasher()
def hash_password(password: str) -> str: return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:  ph.verify(hashed_password, plain_password)
    except Exception: return False

def _now_utc() -> datetime: return datetime.now(timezone.utc)

def create_access_token(*, user_id: str, username: str, token_version: int) -> str:
    expire = _now_utc() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id, "usr": username, "ver": token_version, "type": "access", "exp": expire, "iat": _now_utc(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(*, user_id: str, username: str, token_version: int) -> str:
    expire = _now_utc() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id, "usr": username, "ver": token_version, "type": "refresh", "exp": expire, "iat": _now_utc(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try: return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def user_doc_to_public(user: dict) -> UserPublic:
    return UserPublic(
        id=str(user.get("_id")),
        username=user.get("username"),
        name=user.get("name"),
        email=user.get("email"),
        phone_number=user.get("phone_number"),
        created_at=user.get("created_at")
    )

# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------
async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token")

    user_id = payload.get("sub")
    token_version = payload.get("ver", 0)

    user = db[USERS_COLL].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.get("token_version", 0) != token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    return user

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@router.post("/register", response_model=UserPublic, status_code=201)
async def register(payload: RegisterRequest):
    existing = db[USERS_COLL].find_one({"$or": [{"username": payload.username}, {"email": payload.email}, {"phone_number": payload.phone_number}]})
    if existing:
        if existing.get("username") == payload.username:
            raise HTTPException(status_code=409, detail="Username already exists")
        if existing.get("email") == payload.email:
            raise HTTPException(status_code=409, detail="Email already registered")
        if existing.get("phone_number") == payload.phone_number:
            raise HTTPException(status_code=409, detail="Phone number already registered")

    doc = {
        "username": payload.username,
        "password_hash": hash_password(payload.password),
        "name": payload.name,
        "email": payload.email,
        "phone_number": payload.phone_number,
        "created_at": _now_utc(),
        "token_version": 1
    }
    res = db[USERS_COLL].insert_one(doc)
    doc["_id"] = res.inserted_id
    return user_doc_to_public(doc)

@router.put("/update", response_model=UserPublic)
async def update_account(payload: UpdateAccountRequest, user: dict = Depends(get_current_user)):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates: raise HTTPException(status_code=400, detail="No valid fields to update")

    if "email" in updates:
        existing = db[USERS_COLL].find_one({"email": updates["email"], "_id": {"$ne": user["_id"]}})
        if existing: raise HTTPException(status_code=409, detail="Email already in use")

    if "phone_number" in updates:
        existing = db[USERS_COLL].find_one({"phone_number": updates["phone_number"], "_id": {"$ne": user["_id"]}})
        if existing: raise HTTPException(status_code=409, detail="Phone number already in use")

    db[USERS_COLL].update_one({"_id": user["_id"]}, {"$set": updates})
    user.update(updates)
    return user_doc_to_public(user)

@router.delete("/delete")
async def delete_account(user: dict = Depends(get_current_user)):
    db[USERS_COLL].delete_one({"_id": user["_id"]})
    return {"message": "Account deleted successfully"}

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = db[USERS_COLL].find_one({"username": payload.username})
    if not user: raise HTTPException(status_code=401, detail="Invalid username or password")

    try: ph.verify(user["password_hash"], payload.password)
    except Exception: raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate tokens
    access_token = create_access_token(
        user_id=str(user["_id"]),
        username=user["username"],
        token_version=user.get("token_version", 1)
    )
    refresh_token = create_refresh_token(
        user_id=str(user["_id"]),
        username=user["username"],
        token_version=user.get("token_version", 1)
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
