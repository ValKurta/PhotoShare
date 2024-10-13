from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas import Rating, RatingCreate  # Импортируем схемы для рейтинга
from src.database.models import User
from src.services.rating import add_rating  # Сервис для добавления рейтинга
# from src.services.auth import get_current_user

router = APIRouter(prefix="/photos", tags=["photos"])

@router.post("/photos/{photo_id}/rate", response_model=Rating)
async def rate_photo(
    photo_id: int,
    rating: RatingCreate,  # Схема для ввода данных рейтинга
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Проверка авторизации пользователя
):
    result = await add_rating(db=db, photo_id=photo_id, rating=rating,) #user_id=current_user.id)
    
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фото не найдено")

    return result
