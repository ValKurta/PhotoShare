from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from src.database.models import Photo, Rating


def filter_photos_by_criteria(
    db: Session,
    min_rating: Optional[float],
    max_rating: Optional[float],
    start_date: Optional[str],
    end_date: Optional[str],
) -> List[Photo]:
    query = db.query(Photo)

    if start_date:
        query = query.filter(Photo.created_at >= start_date)
    if end_date:
        query = query.filter(Photo.created_at <= end_date)

    if min_rating is not None or max_rating is not None:
        query = query.outerjoin(Rating).group_by(Photo.id)

        if min_rating is not None:
            query = query.having(func.avg(Rating.rating) >= min_rating)
        if max_rating is not None:
            query = query.having(func.avg(Rating.rating) <= max_rating)

    return query.all()
