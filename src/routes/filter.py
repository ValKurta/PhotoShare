from fastapi import APIRouter, FastAPI, Depends, Query
from sqlalchemy.orm import Session
from services.filter import filter_photos
from database.db import get_db 

router = APIRouter()


@router.get("/photos/filter/")
def filter_photos(
    db: Session = Depends(get_db),
    min_rating: int = Query(None, ge=1, le=5),  # Минимальный рейтинг (1-5)
    max_rating: int = Query(None, ge=1, le=5),  # Максимальный рейтинг (1-5)
    start_date: str = Query(None),  # Дата начала (в формате YYYY-MM-DD)
    end_date: str = Query(None)  # Дата окончания (в формате YYYY-MM-DD)
):

    return filter_photos(db, min_rating=min_rating, max_rating=max_rating, start_date=start_date, end_date=end_date)