from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.models import Photo

def filter_photos_by_criteria(
    db: Session,
    min_rating: Optional[float],
    max_rating: Optional[float],
    start_date: Optional[str],
    end_date: Optional[str]
) -> List[Photo]:
    query = db.query(Photo)

    # Фильтрация по рейтингу
    if min_rating is not None:
        query = query.filter(Photo.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Photo.rating <= max_rating)

    # Фильтрация по дате
    if start_date:
        query = query.filter(Photo.upload_date >= start_date)
    if end_date:
        query = query.filter(Photo.upload_date <= end_date)

    return query.all()
