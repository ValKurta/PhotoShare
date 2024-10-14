from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src import schemas
from database.db import get_db


router = APIRouter()


# Поиск фотографий по тегам
@router.get("/photos/search/tags", response_model=list[schemas.Photo])
def search_photos_by_tags(tags: str, db: Session = Depends(get_db)):
    tags_list = tags.split(",")
    return search_photos_by_tags(db=db, tags=tags_list)


# Поиск по ключевым словам в описании
@router.get("/photos/search/keywords", response_model=list[schemas.Photo])
def search_photos_by_keywords(keywords: str, db: Session = Depends(get_db)):
    return search_photos_by_keywords(db=db, keywords=keywords)
