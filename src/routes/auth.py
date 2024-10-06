from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from src.schemas import UserCreateModel, UserLoginModel, UserDbModel, UserResponseModel, TokenModel, RoleEnum
from src.services.auth import auth_service

router = APIRouter()


@router.post("/auth/signup", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
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
        detail="User has been successfully created"
    )


@router.post("/auth/login", response_model=TokenModel)
async def login_user(user: UserLoginModel):
    # Simulate login and JWT generation
    if user.email == "admin@example.com" and user.password == "fakepass":
        access_token = await auth_service.create_access_token(data={"sub": user.email, "role": "admin"})
        refresh_token = await auth_service.create_refresh_token(data={"sub": user.email, "role": "admin"})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
