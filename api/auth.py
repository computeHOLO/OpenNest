from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("OPENNEST_JWT_SECRET", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
CRED_KEY_PATH = "cred.key"
CRED_STORE_PATH = "cred.store"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

def ensure_store():
    if not os.path.exists(CRED_KEY_PATH):
        with open(CRED_KEY_PATH, "wb") as f:
            f.write(Fernet.generate_key())
    if not os.path.exists(CRED_STORE_PATH):
        raise RuntimeError("Credential store missing. Run first setup to create encrypted credentials.")

def get_fernet():
    ensure_store()
    with open(CRED_KEY_PATH, "rb") as f:
        key = f.read()
    return Fernet(key)

def read_creds():
    f = get_fernet()
    with open(CRED_STORE_PATH, "rb") as s:
        data = s.read()
    payload = f.decrypt(data).decode().split(":")
    return payload[0], payload[1]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        username, hashed = read_creds()
    except Exception:
        raise HTTPException(status_code=500, detail="Auth store not initialized")
    if form_data.username != username or not verify_password(form_data.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username})
    return Token(access_token=token, token_type="bearer")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=sub)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
