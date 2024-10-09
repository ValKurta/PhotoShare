from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from src.schemas import (
    UserCreateModel,
    UserLoginModel,
    UserDbModel,
    UserResponseModel,
    TokenModel,
    RoleEnum,
)
from src.services.auth import auth_service
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.services.auth import auth_service
from src.repository.token_blacklist import add_token_to_blacklist
from src.database.db import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post(
    "/auth/signup",
    response_model=UserResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def signup(user: UserCreateModel):
    # Simulate user registration logic
    new_user = UserDbModel(
        id=1,
        username=user.username,
        email=user.email,
        created_at=datetime.now(),
        role=RoleEnum.user,
        is_active=True,
    )
    return UserResponseModel(
        user=new_user,
        role=new_user.role,
        detail=f"A new '{new_user.role.name}' has been successfully created",
    )


@router.post("/auth/login", response_model=TokenModel)
async def login_user(user: UserLoginModel):
    # Simulate login and JWT generation
    if user.email == "admin@example.com" and user.password == "fakepass":
        access_token = await auth_service.create_access_token(
            data={"sub": user.email, "role": "admin"}
        )
        refresh_token = await auth_service.create_refresh_token(
            data={"sub": user.email, "role": "admin"}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
    )


@router.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    User logout and the addition to the black list of tokens
    """
    await add_token_to_blacklist(token, db)
    return {"detail": "Logged out successfully"}
