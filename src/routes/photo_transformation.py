from typing import List, Any, Coroutine, Union
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form, Query
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from io import BytesIO

from src.database.db import get_db
from src.repository import photo_transformation as repository_effects
from src.repository import photos as repository_photos
from src.photo_effects_schemas import CropEnum, GravityEnum, PhotoEffectResponse
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix="/photo_effects", tags=["photo_effects"])

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


@router.post('/gravity_crop/{photo_id}', response_model=PhotoEffectResponse)
async def change_size(photo_id: int,
                      aspect_ratio: str,
                      width: int,
                      crop: CropEnum = Query(..., description="Choose a parameter"),
                      gravity: GravityEnum = Query(default='auto', description="Choose a parameter"),
                      current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    Change the size of a photo.

    - **photo_id** (int): The ID of the photo.
    - **height** (int): The new height of the photo.
    - **width** (int): The new width of the photo.
    - **crop** (CropEnum): Crop options.
    - **gravity** (GravityEnum): Gravity options.
    - **background** (str): Background options.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the photo is not found or if the dimensions are invalid.

    Returns:
    - **PhotoEffectResponse**: The updated photo details.
    """
    
    # Check validity of dimensions
    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail="Width and height must be positive numbers.")

    # Check gravity and crop combinations
    if gravity != 'auto' and crop not in ['fill', 'crop']:
        raise HTTPException(status_code=400, detail="Gravity can only be used with 'fill' or 'crop' options.")

    resized_photo = await repository_effects.gravity_crop(photo_id, aspect_ratio, width, crop.value, gravity.value,
                                                         current_user, db)
    if resized_photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not changed')

    return resized_photo


@router.post('/coordinates_cropping/{photo_id}', response_model=PhotoEffectResponse)
async def coordinates_crop(photo_id: int,
                           aspect_ratio: str,
                           width: int,
                           x_coordinate: int,
                           y_coordinate: int,
                           crop: CropEnum = Query(..., description="Choose a parameter"),
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):

    transformed_photo = await repository_effects.coordinates_crop(photo_id, aspect_ratio, width, x_coordinate,
                                                                  y_coordinate, crop.value, current_user, db)

    return transformed_photo


@router.post('/reset_transformation/{photo_id}')
async def reset_transformation(photo_id: int,
                               current_user: User = Depends(auth_service.get_current_user),
                               db: Session = Depends(get_db)):

    transformed_photo = await repository_effects.reset_transformation(photo_id, current_user, db)

    return {'photo_url': transformed_photo.url, 'transformed_photo': transformed_photo.url, 'message': 'Transformation was canceled'}


@router.post('/save_transformation/{photo_id}')
async def save_transformation(photo_id: int,
                              current_user: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):

    transformed_photo = await repository_effects.save_transformation(photo_id, current_user, db)

    return {'photo_url': transformed_photo.url, 'transformed_photo': transformed_photo.url, 'message': 'Transformation was saved'}


@router.post('/roll_back_transformations/{photo_id}')
async def roll_back_transformations(photo_id: int,
                                    current_user: User = Depends(auth_service.get_current_user),
                                    db: Session = Depends(get_db)):

    transformed_photo = await repository_effects.roll_back_transformations(photo_id, current_user, db)

    return {'photo_url': transformed_photo.url, 'transformed_photo': transformed_photo.url, 'message': 'All the transformations were canceled'}


@router.post('/get_qr_code/{photo_id}')
async def generate_qr(photo_id: int,
                      current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):

    """
    Generate a QR code for a photo.

    - **photo_id** (int): The ID of the photo.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **StreamingResponse**: The QR code as a PNG image.
    """
    photo = await repository_photos.read_photo(photo_id, current_user, db)
    url = photo.transformed_url

    # Create the object of QR-code
    qr = QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add data into QR-code
    qr.add_data(url)
    qr.make(fit=True)

    # Generate image of qr-code
    img = qr.make_image(fill="black", back_color="white")

    #  saves image in memory buffer
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    # Returns image as StreamingResponse
    return StreamingResponse(img_io, media_type="image/png")

