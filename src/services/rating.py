from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import Photo, Rating
from src.schemas import RatingCreate


async def add_rating(db: Session, photo_id: int, rating: RatingCreate, user_id: int):
    # Находим фото по ID
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    if photo.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are the photo's owner! Rate a photo of other people",
        )

    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating can be between 1 and 5",
        )

    existing_rating = (
        db.query(Rating)
        .filter(Rating.photo_id == photo_id, Rating.user_id == user_id)
        .first()
    )
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have rated this photo already!",
        )

    # Создаем новый рейтинг
    new_rating = Rating(
        photo_id=photo_id,
        user_id=user_id,
        rating=rating.rating,  # Оценка из схемы RatingCreate
    )

    # Добавляем в сессию и сохраняем
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating
