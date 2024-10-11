from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import schemas
from src.database.models import User
from database.db import get_db 
from src.services.rating import add_rating

router = APIRouter()

# Добавить рейтинг
@router.post("/photos/{photo_id}/rate", response_model=schemas.Rating)
def rate_photo(photo_id: int, rating: schemas.RatingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return add_rating(db=db, photo_id=photo_id, rating=rating, user_id=current_user.id)

# Получить средний рейтинг фотографии
@router.get("/photos/{photo_id}/average-rating", response_model=float)
def get_average_rating(photo_id: int, db: Session = Depends(get_db)):
    return get_average_rating(db=db, photo_id=photo_id)