from typing import List, Type

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest

import sqlalchemy.exc
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from src.conf.config import settings
from src.schemas import PhotoModel, PhotoResponse, TagModel, TagsPhoto
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError

from fastapi import UploadFile, HTTPException, status

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


async def create_photo(text: str, url: str, user: User, db: Session) -> Photo:

    photo = Photo(
        user_id=user.id,
        url=url,
        description=text
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def read_photo(photo_id: int, user: User, db: Session) -> Type[Photo] | None:
    return db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()


async def update_photo(photo_id: int, url: UploadFile, description: str, user: User,  db: Session) -> Photo | None:

    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()
    if photo:
        await destroy_cloud_url(photo.url)
        photo.url = url
        photo.description = description
        db.commit()
    return photo


async def delete_photo(photo_id: int, user: User, db: Session) -> Type[Photo]:

    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    if photo:
        await destroy_cloud_url(photo.url)
        db.delete(photo)
        db.commit()
    return photo


async def change_description(photo_id: int, description: str, user: User, db: Session) -> Photo | None:
async def change_description(
    photo_id: int, description: str, db: Session
) -> Photo | None:

    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()
    if photo:
        photo.description = description
        db.commit()
    return photo


async def get_users_photos(user_id: int, user: User, db: Session) -> List[Type[Photo]] | None:
    user = db.query(User).join(Photo).filter(and_(User.id == user_id, Photo.user_id == user.id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    photos = db.query(Photo).filter(Photo.user_id == user_id).all()
    return photos


async def destroy_cloud_url(photo_url):
    url_parts = photo_url.split('/')
    photo_public_id = '/'.join(url_parts[-2:])
    result = cloudinary.uploader.destroy(photo_public_id)
    print(f'The old photo url was destroyed: {result["result"]}')



async def search_photos(tag: str, db: Session) -> list[Photo]:
    photos = db.query(Photo).filter(tag in Photo.tags).all()
    return list(photos)
