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


async def change_size(photo_id: int, height: int, width: int, crop: CropEnum, gravity: GravityEnum, background: str,
                      user: User, db: Session) -> Type[Photo]:  #
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)
    version = await get_image_version(photo_public_id)
    try:
        resized_photo_url = CloudinaryImage(photo_public_id).build_url(
            background=background, gravity=gravity.value, height=height, width=width, crop=crop.value, version=version)
        if resized_photo_url:
            photo.transformed_url = resized_photo_url
            db.commit()
        return photo
    except ResponseValidationError as e:
        print(f'Error {e}')


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




