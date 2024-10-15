import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User
from src.database.db import get_db
from src.services.auth import auth_service
from src.schemas import UserAverageRating, UserDbModel, UserProfilePublic, UserProfileEdit
from src.conf.config import settings
from src.repository import users as repository_users
from src.services.average_rating import get_user_rating

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDbModel)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve the current authenticated user's details.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        UserDbModel: The current user's details.
    """
    return current_user


@router.put("/me/", response_model=UserDbModel)
async def update_my_profile(update_data: UserProfileEdit,
                            current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    if update_data.username and len(update_data.username) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username should be at least 5 characters long."
        )

    if update_data.phone_number and (len(update_data.phone_number) < 10 or not update_data.phone_number.isdigit()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number should be at least 10 characters long and consist only of digits."
        )
    update_data_dict = update_data.model_dump(exclude_unset=True)
    updated_user = await repository_users.update_user_profile(current_user, update_data_dict, db)
    return updated_user


@router.patch('/avatar', response_model=UserDbModel)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'PhotoShare/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'PhotoShare/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.get("/profile/{user_id}", response_model=UserProfilePublic)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username,
        "avatar": user.avatar,
        "role": user.role,
        "created_at": user.created_at
    }


@router.get("/{user_id}/rating", response_model=UserAverageRating)
async def get_user_avg_rating(user_id: int, db: Session = Depends(get_db)):
    res = await get_user_rating(db, user_id)
    if res is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "rating": res}