from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
<<<<<<< HEAD
from enum import Enum
from typing import List, Optional
=======
from typing import List, Optional
from enum import Enum

>>>>>>> origin/develop

class RoleEnum(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"


class UserCreateModel(BaseModel):
    username: str = Field(min_length=5, max_length=50)
    email: EmailStr
    hashed_password: str = Field(min_length=6, max_length=255)
    role: RoleEnum = RoleEnum.user


class UserLoginModel(BaseModel):
    email: EmailStr
    hashed_password: str = Field(min_length=6, max_length=255)


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
    detail: str

    class Config:
        from_attributes = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

<<<<<<< HEAD
class CommentBase(BaseModel):
    photo_id: int
    user_id: int
    text: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: str

class Comment(BaseModel):
    id: int
    text: str
    user_id: int
    photo_id: int
    created_at: str

    class Config:
        from_attributes = True 
=======

class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class TagsPhoto(BaseModel):
    tags: List[str]


class PhotoModel(BaseModel):
    description: Optional[str] = Field(max_length=25)

    class Config:
        from_attributes = True


class PhotoResponse(PhotoModel):
    id: int
    url: str


class UserStatistics(BaseModel):
    user_id: int
    username: str
    num_images: int
    num_comments: int
>>>>>>> origin/develop
