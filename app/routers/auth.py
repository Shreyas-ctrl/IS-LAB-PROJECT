from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.db.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.utils import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# JWT Configuration
JWT_SECRET = "your-secret-key-change-this"  # Change to a secure random string in production
JWT_ALG = "HS256"
ISSUER = "notes-app"


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    password_hash = hash_password(user.password)

    new_user = User(
        username=user.username,
        password_hash=password_hash
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return UserRead.model_validate(new_user)


@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create JWT token
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "sub": str(db_user.id),
        "iss": ISSUER,
        "exp": exp.timestamp()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
