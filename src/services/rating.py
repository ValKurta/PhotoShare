from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import Photo, Rating
from src.schemas import RatingCreate

async def add_rating(db: Session, photo_id: int, rating: RatingCreate, user_id: int):
    # Находим фото по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        return None

    if photo.user_id == user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не можете оценивать свои фотографии")
    
    # Создаем новый рейтинг
    new_rating = Rating(
        photo_id=photo_id,
        user_id=user_id,
        rating=rating.rating  # Оценка из схемы RatingCreate
    )

    # Добавляем в сессию и сохраняем
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating