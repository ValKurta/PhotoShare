from pydantic import BaseModel, Field, EmailStr, conlist
from datetime import datetime
from typing import List, Optional
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
    updated_at: datetime
    role: RoleEnum = RoleEnum.user
    allowed: bool = True
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    confirmed: bool

    class Config:
        from_attributes = True


class UserResponseModel(BaseModel):
    user: UserDbModel
    role: RoleEnum
    detail: str = "A new %new_user.role.name% has been successfully created"

    class Config:
        from_attributes = True


class UserProfilePublic(BaseModel):
    username: str = Field(min_length=5, max_length=50)
    avatar: Optional[str] = None
    role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileEdit(BaseModel):
    username: str
    phone_number: Optional[str] = None


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CommentBase(BaseModel):
    photo_id: int
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


class TagModel(BaseModel):
    name: str = Field(max_length=25)

    def __str__(self):
        return self.name


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class TagsPhoto(BaseModel):
    tags: List[str]


class PhotoModel(BaseModel):
    description: str


class PhotoResponse(PhotoModel):
    id: int
    url: str
    tags: List[TagModel]


class UserStatistics(BaseModel):
    user_id: int
    username: str
    num_images: int
    num_comments: int
    rating: float
    average_rating_given: float

class UserAverageRating(BaseModel):
    user_id: int
    rating: float

class RatingCreate(BaseModel):
    rating: int = Field(ge=0, le=5)

class Rating(RatingCreate):
    id: int
    user_id: int
    photo_id: int

    class Config:
        from_attributes = True


class PhotoWithRatingResponse(BaseModel):
    id: int
    url: str
    description: Optional[str]
    rating: Optional[float]

    class Config:
        from_attributes = True
