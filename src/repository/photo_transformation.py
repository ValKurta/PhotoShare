import re
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
from src.photo_effects_schemas import CropEnum, GravityEnum, ColorEffectEnum
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
    existing_params = await parse_transformation(photo.transformed_url)
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(
        transformation=[existing_params, {'gravity': gravity, 'aspect_ratio': aspect_ratio, 'width': width, 'crop': crop}],
        version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def coordinates_crop(photo_id: int, aspect_ratio: str, width: int, x: int, y: int, crop: str,
                           user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'x': x, 'y': y, 'aspect_ratio': aspect_ratio, 'width': width, 'crop': crop, })
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def resize_with_ratio(photo_id: int, aspect_ratio: str, width: int, user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)
    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'aspect_ratio': aspect_ratio, 'width': width})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def cropping(photo_id: int, crop: str, user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'crop': crop})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def color_effects(photo_id: int, color_effect: ColorEffectEnum, additional_parameter: str, user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    effect = ':'.join([color_effect, additional_parameter])

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'effect': effect})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def special_effects(photo_id: int, color_effect: ColorEffectEnum, additional_parameter: str,
                          user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    effect = ':'.join([color_effect, additional_parameter])

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'effect': effect})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def blur_effects(photo_id: int, color_effect: ColorEffectEnum, additional_parameter: str,
                       user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    effect = ':'.join([color_effect, additional_parameter])

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'effect': effect})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def camera(photo_id: int, position: str, image_format: str, user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    effect = position

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'effect': effect, 'format': image_format})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
    return photo


async def background_removal(photo_id: int, effect: ColorEffectEnum,
                             user: User, db: Session) -> Type[Photo]:
    photo = db.query(Photo).join(User).filter(and_(Photo.id == photo_id, User.id == user.id)).first()
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo was not found')
    photo_public_id = await get_public_id(photo.url)

    existing_params = await parse_transformation(photo.transformed_url)
    existing_params.append({'effect': effect})
    version = await get_image_version(photo_public_id)

    resized_photo_url = CloudinaryImage(photo_public_id).build_url(transformation=existing_params, version=version)
    if resized_photo_url:
        photo.transformed_url = resized_photo_url
        db.commit()
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
        transformation = result.get('transformation')
        print(transformation)
        return version
    except cloudinary.exceptions.Error as e:
        print(f"Error while getting photo metadata: {e}")
        return None


async def parse_transformation(url: str) -> list:
    pattern = r"upload/(.*?)/v\d+"
    match = re.search(pattern, url)

    key_mapping = {'ar': 'aspect_ratio', 'w': 'width', 'h': 'height', 'c': 'crop', 'g': 'gravity',
                   'l': 'overlay', 'o': 'opacity', 'e': 'effect', 'dpr': 'dpr', 'fl': 'flags'}

    if match:
        transformation_string = match.group(1)
        # Разделение параметров по ','
        transformations = transformation_string.split('/')
        parsed_transformations_list = []

        # Обработка каждого набора параметров
        for transformation in transformations:
            # Проверяем, есть ли параметры
            params = transformation.split(',')
            parsed_dict = {}
            renamed_transformations = {}
            # Парсинг параметров
            for param in params:
                try:
                    key, value = param.split('_', 1)
                    parsed_dict[key] = value  # Добавляем в словарь
                except ValueError:
                    continue  # Пропускаем некорректные параметры

                renamed_transformations = {key_mapping.get(k, k): v for k, v in parsed_dict.items()}
            # Добавляем словарь в список, если он не пустой
            if parsed_dict:
                parsed_transformations_list.append(renamed_transformations)

        return parsed_transformations_list

    else:
        return []
