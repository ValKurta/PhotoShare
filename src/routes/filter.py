from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.db import get_db
from src.schemas import PhotoModel
from src.services.filter import filter_photos_by_criteria 
from src.services.auth import get_current_user 
from src.database.models import User


router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/photos", response_model=List[PhotoModel])
async def filter_photos(
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Минимальный рейтинг (0-5)"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Максимальный рейтинг (0-5)"),
    start_date: Optional[str] = Query(None, description="Дата начала (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Дата конца (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # если авторизация
):
    photos = filter_photos_by_criteria(db, min_rating, max_rating, start_date, end_date)

    if not photos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фотографии не найдены")
    
    return photos
