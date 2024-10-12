from fastapi import APIRouter, HTTPException, status, Depends, Security
from src.schemas import (
    UserCreateModel,
    UserResponseModel,
    TokenModel,
    RoleEnum,
)
from src.services.auth import auth_service
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.repository import users as repository_users
from src.repository.token_blacklist import add_token_to_blacklist
from src.database.db import get_db
from src.database.models import User
from pydantic import BaseModel
from src.routes.permissions import is_admin


router = APIRouter(prefix='/auth', tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Custom OAuth2 form to use email instead of username
class OAuth2EmailRequestForm(OAuth2PasswordRequestForm):
    def __init__(self, email: str = None, password: str = None):
        super().__init__(username=email, password=password)


@router.post(
    "/signup",
    response_model=UserResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def signup(user: UserCreateModel, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(user.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    user_count = await repository_users.get_user_count(db)
    if user_count == 0:
        role = RoleEnum.admin
    else:
        role = RoleEnum.user

    hashed_password = auth_service.get_password_hash(user.hashed_password)

    user_data = user.model_dump()
    user_data["role"] = role
    user_data["hashed_password"] = hashed_password

    new_user = await repository_users.create_user(user_data, db)

    response_data = UserResponseModel(
        user=new_user,
        role=new_user.role,
        detail="User successfully created"
    )
    return response_data


@router.post(
    "/login",
    response_model=TokenModel
)
async def login_user(user: OAuth2EmailRequestForm = Depends(), db: Session = Depends(get_db)):
    user_login = await repository_users.get_user_by_email(user.username, db)
    if user_login is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(user.password, user_login.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_access_token(data={"sub": user_login.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user_login.email})
    await repository_users.update_token(user_login, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get(
    "/refresh_token",
    response_model=TokenModel
)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme), db: Session = Depends(get_db)):
    if hasattr(credentials, 'credentials'):
        token = credentials.credentials
    else:
        token = credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/auth/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    User logout and the addition to the black list of tokens
    """
    await add_token_to_blacklist(token, db)
    return {"detail": "Logged out successfully"}


# Use RoleEnum for role validation
class RoleUpdateModel(BaseModel):
    role: RoleEnum


@router.put("/update-role/{user_id}")
async def update_user_role(
    user_id: int, role_data: RoleUpdateModel,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    is_admin(current_user)

    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = role_data.role
    await repository_users.update_user_in_db(user, db)

    return {"msg": f"User {user.username}'s role updated to {user.role}"}
