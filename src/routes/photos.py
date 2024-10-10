import datetime
import os
import pickle

from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.repository import photos as repository_photos
from src.schemas import PhotoResponse, PhotoModel, TagsPhoto
from src.conf.config import settings

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post('/', response_model=PhotoResponse)
async def create_photo(file: UploadFile = File(),
                       description: str = Form(),
                       db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    r = cloudinary.uploader.upload(file.file,
                                   public_id=f'PhotoShare/{description[:7].replace(" ", "") +
                                                           file.filename.replace(".", "")}',
                                   overwrite=True)
    url = cloudinary.CloudinaryImage(f'PhotoShare/{description[:7].replace(" ", "") +
                                                   file.filename.replace(".", "")}') \
        .build_url(crop='fill', version=r.get('version'))

    return await repository_photos.create_photo(description, url, db)


@router.get('/{photo_id}', response_model=PhotoResponse)
async def read_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = await repository_photos.read_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


@router.put('/{photo_id}', response_model=PhotoResponse)
async def update_photo(photo_id: int,
                       file: UploadFile = File(),
                       description: str = Form(),
                       db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    r = cloudinary.uploader.upload(file.file,
                                   public_id=f'PhotoShare/{description[:7].replace(" ", "") +
                                                           file.filename.replace(".", "")}',
                                   overwrite=True)
    url = cloudinary.CloudinaryImage(f'PhotoShare/{description[:7].replace(" ", "") +
                                                   file.filename.replace(".", "")}') \
        .build_url(crop='fill', version=r.get('version'))

    photo = await repository_photos.update_photo(photo_id, url, description, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo


@router.delete('/{photo_id}', response_model=PhotoResponse)
async def delete_photo(photo_id: int,
                       db: Session = Depends(get_db)):

    photo = await repository_photos.delete_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo


@router.patch('/{photo_id}', response_model=PhotoResponse)
async def change_description(photo_id: int,
                             description: str,
                             db: Session = Depends(get_db)):

    photo = await repository_photos.change_description(photo_id, description, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo
