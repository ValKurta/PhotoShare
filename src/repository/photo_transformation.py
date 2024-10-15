from typing import List, Type
from pydantic import validator, field_validator
from fastapi.exceptions import ResponseValidationError

from cloudinary import CloudinaryImage
import cloudinary.api
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest

import sqlalchemy.exc
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from src.conf.config import settings
from src.schemas import PhotoModel, PhotoResponse, TagModel, TagsPhoto
from src.photo_effects_schemas import CropEnum, GravityEnum
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError

from qrcode import QRCode

from fastapi import UploadFile, HTTPException, status

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


async def gravity_crop(photo_id: int, aspect_ratio: str, width: int, crop: str, gravity: str,
                       user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    version = await get_image_version(photo_public_id)
    try:
        resized_photo_url = CloudinaryImage(photo_public_id).build_url(gravity=gravity,
                                                                       aspect_ratio=aspect_ratio,
                                                                       width=width, crop=crop,
                                                                       version=version)
        if resized_photo_url:
            photo.transformed_url = resized_photo_url
            db.commit()
        return photo
    except ResponseValidationError as e:
        print(f'Error {e}')

    return photo


async def coordinates_crop(photo_id: int, aspect_ratio: str, width: int, x: int, y: int, crop: str,
                           user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    version = await get_image_version(photo_public_id)
    try:
        resized_photo_url = CloudinaryImage(photo_public_id).build_url(aspect_ratio=aspect_ratio,
                                                                       width=width, crop=crop, x=x, y=y,
                                                                       version=version)
        if resized_photo_url:
            photo.transformed_url = resized_photo_url
            db.commit()
        return photo
    except ResponseValidationError as e:
        print(f'Error {e}')

    return photo


async def reset_transformation(photo_id: int, user: User, db: Session):
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    photo.transformed_url = photo.url
    db.commit()
    return photo


async def save_transformation(photo_id: int, user: User, db: Session):
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    photo.url = photo.transformed_url
    db.commit()
    return photo


async def roll_back_transformations(photo_id: int, user: User, db: Session):
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    photo_public_id = await get_public_id(photo.url)
    version = await get_image_version(photo_public_id)
    try:
        url = cloudinary.CloudinaryImage(photo_public_id).build_url(
            version=version
        )
        if url:
            photo.transformed_url = url
            photo.url = url
            db.commit()
        return photo
    except ResponseValidationError as e:
        print(f'Error {e}')

    photo.url = photo.transformed_url
    return photo


async def get_public_id(url: str) -> str:
    url_parts = url.split('/')
    photo_public_id = '/'.join(url_parts[-2:])
    return photo_public_id


# Get info on cloudinary about th photo
async def get_image_version(public_id):
    try:
        # Take metadata by public_id
        result = cloudinary.api.resource(public_id)
        # Take the photo version
        version = result.get('version')
        return version
    except cloudinary.exceptions.Error as e:
        print(f"Error while getting photo metadata: {e}")
        return None




