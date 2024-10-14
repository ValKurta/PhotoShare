from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import Rating, RatingCreate
from src.database.models import User, Photo
from src.services.rating import add_rating
from src.services.auth import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/{photo_id}/rate", response_model=Rating)
async def rate_photo(
    photo_id: int,
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found!"
        )
    if photo.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are the photo's owner! Rate a photo of other people",
        )

    result = await add_rating(
        db=db, photo_id=photo_id, rating=rating, user_id=current_user.id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found!"
        )

    return result
