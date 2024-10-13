from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest

from src.database.db import get_db
from src.repository import photos as repository_photos
from src.schemas import PhotoResponse, PhotoModel, TagsPhoto, TagModel
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix="/photos", tags=["photos"])

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

# TODO: fetch all photos

@router.post('/post_photo', response_model=PhotoResponse)
async def create_photo(file: UploadFile = File(),
                       description: str = Form(),
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    # Create a clean file identifier
    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    user_name = current_user.username
    public_id = f'PhotoShare/{user_name}{clean_description}{clean_filename}'

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(crop='fill', version=r.get('version'))

        return await repository_photos.create_photo(description, url, current_user, db)
    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.get('/get_photo/{photo_id}', response_model=PhotoResponse)
async def read_photo(photo_id: int,
                     current_user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    photo = await repository_photos.read_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


@router.put('/update_photo/{photo_id}', response_model=PhotoResponse)
async def update_photo(photo_id: int,
                       file: UploadFile = File(),
                       description: str = Form(),
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):

    # Create a clean file identifier
    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    user_name = current_user.username
    public_id = f'PhotoShare/{user_name}{clean_description}{clean_filename}'

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(crop='fill', version=r.get('version'))
        photo = await repository_photos.update_photo(photo_id, url, description, current_user, db)

        if photo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
        return photo

    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.delete('/delete_photo/{photo_id}')
async def delete_photo(photo_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    photo = await repository_photos.delete_photo(photo_id, current_user, db)
    return {'photo': photo, 'message': 'was successfully deleted'}


@router.patch('/add_description/{photo_id}', response_model=PhotoResponse)
async def change_description(photo_id: int,
                             description: str = Form(),
                             current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):

    photo = await repository_photos.change_description(photo_id, description, current_user, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo


@router.get('/get_users_photos/{user_id}', response_model=List[PhotoResponse])
async def get_users_photos(user_id: int,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    photos = await repository_photos.get_users_photos(user_id, current_user, db)
    if len(photos) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User didn't post any photos")
    return photos


@router.get('/get_my_photos/', response_model=List[PhotoResponse])
async def get_my_photos(current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    photos = await repository_photos.get_users_photos(current_user.id, current_user, db)
    if len(photos) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User didn't post any photos")
    return photos
