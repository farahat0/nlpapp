from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import verify_token
from backend.modules.auth.schemas import UserCreate, UserLogin, UserOut, Token
from backend.modules.auth.service import register_user, authenticate_user, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user = register_user(user_data.username, user_data.password, db)
    return user


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and receive a JWT token."""
    token = authenticate_user(form_data.username, form_data.password, db)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def get_me(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user's info."""
    user = get_current_user(username, db)
    return user
