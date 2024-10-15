from fastapi import APIRouter, HTTPException, status, Depends, Security, BackgroundTasks, Request
from fastapi import APIRouter, HTTPException, status, Depends, Security, Form
from jose import JWTError, jwt

from src.schemas import (
    UserCreateModel,
    UserResponseModel,
    TokenModel,
    RoleEnum,
)
from src.services.auth import auth_service
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.orm import Session
from src.repository import users as repository_users
from src.repository.token_blacklist import add_token_to_blacklist
from src.database.db import get_db
from src.database.models import User
from pydantic import BaseModel
from src.routes.permissions import is_admin
from src.conf.config import settings
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post(
    "/signup",
    response_model=UserResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def signup(user: UserCreateModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **user** (UserCreateModel): The user information for registration.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: 409 error if the user already exists.

    Returns:
    - **UserResponseModel**: The newly created user's data.
    """
    exist_user = await repository_users.get_user_by_email(user.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )

    user_count = await repository_users.get_user_count(db)
    if user_count == 0:
        role = RoleEnum.admin
    else:
        role = RoleEnum.user

    hashed_password = auth_service.get_password_hash(user.password)

    user_data = user.model_dump()
    user_data.pop("password")
    user_data["hashed_password"] = hashed_password
    user_data["role"] = role

    new_user = await repository_users.create_user(user_data, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)

    response_data = UserResponseModel(
        user=new_user,
        role=new_user.role,
        detail="User successfully created. Check your email for confirmation."
    )
    return response_data


@router.post("/login", response_model=TokenModel)
async def login_user(
    user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Log in the user and generate access and refresh tokens.

    - **user** (OAuth2PasswordRequestForm): The login credentials.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the email or password is invalid.

    Returns:
    - **TokenModel**: The access and refresh tokens for the user.
    """

    user_login = await repository_users.get_user_by_email(user.username, db)
    if not user_login.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    if user_login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not auth_service.verify_password(user.password, user_login.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    access_token = await auth_service.create_access_token(
        data={"sub": user_login.email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user_login.email}
    )
    await repository_users.update_token(user_login, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Refresh the access token using a valid refresh token.

    - **credentials** (HTTPAuthorizationCredentials): The authorization credentials with the refresh token.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the refresh token is invalid or mismatched.

    Returns:
    - **TokenModel**: The new access and refresh tokens.
    """

    if hasattr(credentials, "credentials"):
        token = credentials.credentials
    else:
        token = credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Log out the user and add the token to the blacklist.

    - **token** (str): The access token.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the token is invalid.

    Returns:
    - **dict**: A confirmation message for successful logout.
    """

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
        await add_token_to_blacklist(token, db)
        return {"detail": f"User has logged out successfully."}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# Use RoleEnum for role validation
class RoleUpdateModel(BaseModel):
    role: RoleEnum


@router.put("/update-role/{user_id}")
async def update_user_role(
    user_id: int,
    role_data: RoleUpdateModel,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the role of a user (admin only).

    - **user_id** (int): The ID of the user whose role needs to be updated.
    - **role_data** (RoleUpdateModel): The new role for the user.
    - **current_user** (User, optional): The current authenticated admin user.
    - **db** (Session, optional): Dependency for the database session.

    Raises:
    - **HTTPException**: If the user is not found or if the current user is not an admin.

    Returns:
    - **dict**: A confirmation message for successful role update.
    """
    is_admin(current_user)

    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.role = role_data.role
    await repository_users.update_user_in_db(user, db)

    return {"msg": f"User {user.username}'s role updated to {user.role}"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email.

    - **token** (str): The security token for email confirmation.
    - **db** (Session): The database session.

    Raises:
    - **HTTPException**: If the user is not found or if the user's email is already confirmed.

    Returns:
    - **dict**: A confirmation message for successful email confirmation.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}
