from src.database.models import User, Photo, Comment
from src.schemas import UserStatistics
from sqlalchemy.orm import Session

from typing import List, Type
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from src.schemas import PhotoModel, PhotoResponse, TagModel, TagsPhoto
from datetime import date, timedelta

from fastapi import UploadFile

from src.services.average_rating import get_average_rating_user_gives, get_user_rating


async def create_photo(user_id:int, text: str, url: str, db: Session) -> Photo:

    photo = Photo(
        user_id=user_id,
        url=url,
        description=text
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def read_photo(photo_id: int, db: Session) -> Type[Photo] | None:
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def update_photo(photo_id: int, url: UploadFile, description: str, db: Session) -> Photo | None:

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        photo.url = url
        photo.description = description
        db.commit()
    return photo


async def delete_photo(photo_id: int, db: Session) -> Photo | None:

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        db.delete(photo)
        db.commit()
    return photo


async def change_description(photo_id: int, description: str, db: Session) -> Photo | None:

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        photo.description = description
        db.commit()
    return photo


async def add_tags(photo_id: int, body: TagsPhoto, db: Session) -> Photo | None:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    photo_tags = photo.tags

    for tag in body.tags:
        if len(photo_tags) < 5:
            photo.add_tag(photo_id, tag, db)
        else:

            break

    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if photo:
        photo.tags = body.tags
        db.commit()
    return photo


async def add_tag(photo_id: int, tag: str, db: Session) -> Photo | None:
    pass


async def search_photos(tag: str, db: Session) -> list[Photo]:
    photos = db.query(Photo).filter(tag in Photo.tags).all()
    return list(photos)

async def get_user_statistics(db: Session):
    """
    Retrieve statistics for all users in the system.

    Args:
    - **db** (Session): Database session dependency.

    Returns:
    - **List[UserStatistics]**: A list of user statistics.
    """
    statistics = []
    users = db.query(User).all()

    for user in users:
        user_stats = UserStatistics(
            user_id=user.id,
            username=user.username,
            num_images=db.query(Photo).filter(Photo.user_id == user.id).count(),
            num_comments=db.query(Comment).filter(Comment.user_id == user.id).count(),
            rating = await get_user_rating(db, user.id),
            average_rating_given=await get_average_rating_user_gives(db, user.id),
        )
        statistics.append(user_stats)

    return statistics


async def block_user(user_id: int, db: Session) -> User | None:
    """
    Blocks a user in the system.

    Args:
    - **user_id** (int): The ID of the user to block.
    - **db** (Session): Database session dependency.

    Returns:
    - **User | None**: The blocked user or None if the user is not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.allowed = False
        db.commit()
    return user

async def unblock_user(user_id: int, db: Session) -> User | None:
    """
    Unblocks a user in the system.

    Args:
    - **user_id** (int): The ID of the user to unblock.
    - **db** (Session): Database session dependency.

    Returns:
    - **User | None**: The unblocked user or None if the user is not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.allowed = True
        db.commit()
    return user
