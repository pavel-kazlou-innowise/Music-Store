from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..models.database import get_db
from ..models.models import User
from ..schemas.schemas import UserCreate, UserResponse, Token
from ..utils.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    get_current_admin_user
)
from ..core.config import settings

router = APIRouter(tags=["authentication"])

# Схема для обновления прав пользователя
class UserRightsUpdate(BaseModel):
    is_admin: bool

@router.post("/register", response_model=UserResponse, responses={200: {"content": {"application/json": {}}}})
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    First registered user automatically becomes an admin.
    """
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Check if this is the first user
    is_first_user = db.query(User).first() is None
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=is_first_user  # Первый пользователь становится админом
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return Response(content=UserResponse.model_validate(db_user).model_dump_json(), media_type="application/json")

@router.post("/token", response_model=Token, responses={200: {"content": {"application/json": {}}}})
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Response(content=Token(access_token=access_token, token_type="bearer").model_dump_json(), media_type="application/json")

@router.patch("/users/{username}/rights", response_model=UserResponse, responses={200: {"content": {"application/json": {}}}})
def update_user_rights(
    username: str,
    rights: UserRightsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update user rights (Admin only)
    """
    # Проверяем, что пользователь не пытается изменить свои права
    if current_user.username == username:
        raise HTTPException(
            status_code=400,
            detail="Cannot modify your own admin rights"
        )
    
    # Находим пользователя
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Обновляем права
    user.is_admin = rights.is_admin
    db.commit()
    db.refresh(user)
    return Response(content=UserResponse.model_validate(user).model_dump_json(), media_type="application/json")
