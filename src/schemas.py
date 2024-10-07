from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class UserCreateModel(BaseModel):
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=255)


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=255)


class UserDbModel(BaseModel):
    id: int
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    created_at: datetime
    role: RoleEnum = RoleEnum.user
    is_active: bool = True

    class Config:
        from_attributes = True


class UserResponseModel(BaseModel):
    user: UserDbModel
    role: RoleEnum
    detail: str = "A new %new_user.role.name% has been successfully created"

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
