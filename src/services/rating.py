from sqlalchemy.orm import Session
from sqlalchemy import func
from src import schemas
from src.database.models import Photo, Rating


# Добавить рейтинг
def add_rating(db: Session, user_id: int, photo_id: int, rating_value: int):
    photo_owner = db.query(Photo.user_id).filter(Photo.id == photo_id).first()
    if photo_owner and photo_owner.user_id == user_id:
        raise ValueError("Вы не можете оценивать собственные фотографии.")
    
    existing_rating = db.query(Rating).filter(
        Rating.user_id == user_id,
        Rating.photo_id == photo_id
    ).first()

    if existing_rating:
        raise ValueError("Вы уже оценили эту фотографию.")

    new_rating = Rating(user_id=user_id, photo_id=photo_id, rating=rating_value)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

# Получить средний рейтинг фотографии
def get_average_rating(db: Session, photo_id: int):
    avg_rating = db.query(func.avg(Rating.rating)).filter(Rating.photo_id == photo_id).scalar()
    return avg_rating or 0