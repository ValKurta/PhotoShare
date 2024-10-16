from typing import List, Any, Coroutine, Union
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import cloudinary.uploader
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from io import BytesIO

from src.database.db import get_db
from src.repository import photo_transformation as repository_effects
from src.repository import photos as repository_photos
from src.photo_effects_schemas import (CropEnum, GravityEnum, PhotoEffectResponse, CameraEffect, ColorEffectEnum,
                                       BlurEffect, SpecialEffectsEnum, BackgroundEffect)
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
    Change size of photo.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **aspect_ratio** (str): Ratio between width and height(1.5, 3:4).
    - **width** (int): width of image.
    - **crop** (CropEnum): cropping mode.
    - **gravity** (GravityEnum): specify the focus.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    # Check validity of dimensions
    if width <= 0:
        raise HTTPException(status_code=400, detail="Height must be positive numbers.")

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
    """
    Cropping photo by coordinates.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **aspect_ratio** (str): Ratio between width and height(1.5, 3:4).
    - **width** (int): width of image.
    - **crop** (CropEnum): cropping mode.
    - **x_coordinate** (int): x coordinate.
    - **y_coordinate** (int): y coordinate.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.coordinates_crop(photo_id, aspect_ratio, width, x_coordinate,
                                                                  y_coordinate, crop.value, current_user, db)

    return transformed_photo


@router.post('/resize_with_ratio/{photo_id}', response_model=PhotoEffectResponse)
async def resize_with_ratio(photo_id: int,
                            aspect_ratio: str,
                            width: int,
                            current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    """
    Change size of photo.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **spect_ratio** (str): Ratio between width and height(1.5, 3:4).
    - **width** (int): width of image.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.resize_with_ratio(photo_id, aspect_ratio, width, current_user, db)

    return transformed_photo


@router.post('/cropping/{photo_id}', response_model=PhotoEffectResponse)
async def cropping(photo_id: int,
                   crop: CropEnum = Query(..., description="Choose a parameter"),
                   current_user: User = Depends(auth_service.get_current_user),
                   db: Session = Depends(get_db)):
    """
    Cropping of the photo.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **crop** (CropEnum): The Cropping mode.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.cropping(photo_id, crop.value, current_user, db)

    return transformed_photo


@router.post('/color_effects/{photo_id}', response_model=PhotoEffectResponse)
async def color_effects(photo_id: int,
                        additional_parameter: str,
                        effect: ColorEffectEnum = Query(..., description="Choose a parameter"),
                        current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
   Implement color effects.

   Args:
   - **photo_id** (int): The photo file to be resized.
   - **additional_parameter** (str): additional parameter for effect (level: -100 +100).
   - **effect** (ColorEffectEnum): implemented effects.
   - **current_user** (User): The current authenticated user.
   - **db** (Session): Database session dependency.

   Returns:
       Photo: The photo details.
    """

    transformed_photo = await repository_effects.color_effects(photo_id, effect.value, additional_parameter, current_user, db)

    return transformed_photo


@router.post('/special_effects/{photo_id}', response_model=PhotoEffectResponse)
async def special_effects(photo_id: int,
                          additional_parameter: str,
                          effect: SpecialEffectsEnum = Query(..., description="Choose a parameter"),
                          current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    """
   Implement color effects.

   Args:
   - **photo_id** (int): The photo file to be resized.
   - **additional_parameter** (str): additional parameter for effect (level: 0-100).
   - **effect** (SpecialEffectsEnum): implemented effects.
   - **current_user** (User): The current authenticated user.
   - **db** (Session): Database session dependency.

   Returns:
       Photo: The photo details.
    """

    transformed_photo = await repository_effects.special_effects(photo_id, effect.value, additional_parameter,
                                                                 current_user, db)

    return transformed_photo


@router.post('/blur_effects/{photo_id}', response_model=PhotoEffectResponse)
async def blur_effects(photo_id: int,
                       additional_parameter: str,
                       effect: BlurEffect = Query(..., description="Choose a parameter"),
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    Implement blur effects.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **additional_parameter** (str): additional parameter for blur (level: 0-1000).
    - **effect** (BlurEffect): implemented effects.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.special_effects(photo_id, effect.value, additional_parameter,
                                                                 current_user, db)

    return transformed_photo


@router.post('/camera/{photo_id}', response_model=PhotoEffectResponse)
async def camera(photo_id: int,
                 up: str,
                 right: str,
                 zoom: str,
                 exposure: str,
                 image_format: str,
                 current_user: User = Depends(auth_service.get_current_user),
                 db: Session = Depends(get_db)):
    """
    Create a view on the image from the camera.

    Args:
    - **photo_id** (str): The photo file to be resized.
    - **up** (str): angle up-down of the camera -90 +90.
    - **right** (str): angle right-left of the camera -90 +90.
    - **zoom** (str): camera zoom for example 1.2.
    - **exposure** (str): exposure of the camera for example 1.8
    - **image_format** (str): format of the image.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """
    up = 'up_' + up
    right = 'right_' + right
    zoom = 'zoom_' + zoom
    exposure = 'exposure_' + exposure
    position = 'camera:' + ';'.join([up, right, zoom, exposure])
    print(position)

    transformed_photo = await repository_effects.camera(photo_id, position, image_format, current_user, db)

    return transformed_photo


@router.post('/reset_transformation/{photo_id}')
async def reset_transformation(photo_id: int,
                               current_user: User = Depends(auth_service.get_current_user),
                               db: Session = Depends(get_db)):
    """
    Reset photo transformations.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.reset_transformation(photo_id, current_user, db)

    return {'photo_url': transformed_photo.url, 'transformed_photo': transformed_photo.url,
            'message': 'Transformation was canceled'}


@router.post('/save_transformation/{photo_id}')
async def save_transformation(photo_id: int,
                              current_user: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):
    """
    Saves photo transformations.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.save_transformation(photo_id, current_user, db)

    return {'photo_url': transformed_photo.url, 'transformed_photo': transformed_photo.url, 'message': 'Transformation was saved'}


@router.post('/roll_back_transformations/{photo_id}')
async def roll_back_transformations(photo_id: int,
                                    current_user: User = Depends(auth_service.get_current_user),
                                    db: Session = Depends(get_db)):
    """
    Rolls back photo to original view.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
    """

    transformed_photo = await repository_effects.roll_back_transformations(photo_id, current_user, db)

    return {'photo_url': transformed_photo.url, 'transformed_photo': transformed_photo.url,
            'message': 'All the transformations were canceled'}


@router.post('/get_qr_code/{photo_id}')
async def generate_qr(photo_id: int,
                      current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    Generates qr-code for transformed photo.

    Args:
    - **photo_id** (int): The photo file to be resized.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
        Photo: The photo details.
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

