from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlmodel import Session, select
from app.models.user import User
from app.db.database import engine

security = HTTPBearer(auto_error=True)
JWT_SECRET = "your-secret-key-change-this"  # MUST MATCH auth.py
JWT_ALG = "HS256"
ISSUER = "notes-app"

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], options={"verify_aud": False})
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("iss") != ISSUER:
        raise HTTPException(status_code=401, detail="Invalid issuer")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid subject")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == int(user_id))).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
