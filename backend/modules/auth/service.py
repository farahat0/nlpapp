from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.modules.auth.model import User
from backend.core.security import hash_password, verify_password, create_access_token


def register_user(username: str, password: str, db: Session) -> User:
    """Register a new user. Raises 400 if username already exists."""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(username: str, password: str, db: Session) -> str:
    """Authenticate user and return JWT token. Raises 401 on failure."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(data={"sub": user.username})
    return token


def get_current_user(username: str, db: Session) -> User:
    """Get the current user by username. Raises 404 if not found."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
