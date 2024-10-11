from sqlalchemy.orm import Session
from src.database.models import Photo, Rating

def filter_photos(db: Session, min_rating: int = None, max_rating: int = None, start_date: str = None, end_date: str = None):
    query = db.query(Photo)

# Фильтрация по рейтингу
    if min_rating is not None:
        query = query.join(Rating).filter(Rating.rating >= min_rating)
    if max_rating is not None:
        query = query.join(Rating).filter(Rating.rating <= max_rating)

    # Фильтрация по дате
    if start_date is not None:
        query = query.filter(Photo.created_at >= start_date)
    if end_date is not None:
        query = query.filter(Photo.created_at <= end_date)

    photos = query.all()
    return photos