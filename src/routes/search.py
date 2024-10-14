from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.schemas import PhotoResponse
from src.services.search import search_photos
from src.database.db import get_db

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get('/photos/search', response_model=List[PhotoResponse])
async def search_photos_route(tag: str = None, keyword: str = None, db: Session = Depends(get_db)):
    if not tag and not keyword:
        raise HTTPException(status_code=400, detail="At least one of 'tag' or 'keyword' must be provided")

    photos = await search_photos(tag, keyword, db)

    return photos
