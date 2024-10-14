from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.db import get_db
from src.schemas import PhotoWithRatingResponse
from src.services.filter import filter_photos_by_criteria
from datetime import date
from pydantic import TypeAdapter
from sqlalchemy import func
from src.database.models import Rating

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/filter", response_model=List[PhotoWithRatingResponse])
async def filter_photos(
    min_rating: Optional[float] = Query(
        None, ge=0, le=5, description="Минимальный рейтинг (0-5)"
    ),
    max_rating: Optional[float] = Query(
        None, ge=0, le=5, description="Максимальный рейтинг (0-5)"
    ),
    start_date: Optional[str] = Query(None, description="Дата начала (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Дата конца (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    try:
        date_adapter = TypeAdapter(Optional[date])
        start_date_parsed = (
            date_adapter.validate_python(start_date) if start_date else None
        )
        end_date_parsed = date_adapter.validate_python(end_date) if end_date else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong date format!"
        )

    photos = filter_photos_by_criteria(
        db, min_rating, max_rating, start_date_parsed, end_date_parsed
    )

    if not photos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo(s) not found!"
        )

    result = []
    for photo in photos:
        avg_rating = (
            db.query(func.avg(Rating.rating))
            .filter(Rating.photo_id == photo.id)
            .scalar()
            or 0
        )
        result.append(
            {
                "id": photo.id,
                "url": photo.url,
                "description": photo.description,
                "rating": round(avg_rating, 2),
            }
        )

    return result
