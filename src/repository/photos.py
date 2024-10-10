from typing import List, Type
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from src.schemas import PhotoModel, PhotoResponse, TagModel, TagsPhoto
from datetime import date, timedelta

from fastapi import UploadFile


async def create_photo(text: str, url: str, db: Session) -> Photo:

    photo = Photo(
        user_id=1,
        url=url,
        description=text
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def read_photo(photo_id: int, db: Session) -> Photo | None:
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
    if photo:
        photo.tags = body.tags
        db.commit()
    return photo


async def search_photos(tag: str, db: Session) -> list[Photo]:
    photos = db.query(Photo).filter(tag in Photo.tags).all()
    return list(photos)