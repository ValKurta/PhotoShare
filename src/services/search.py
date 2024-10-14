from sqlalchemy.orm import Session
from sqlalchemy import func
from src import schemas
from src.database import models


# Поиск фотографий по тегам
def search_photos_by_tags(db: Session, tags: list[str]):
    return (
        db.query(models.Photo)
        .join(models.Photo.tags)
        .filter(models.Tag.name.in_(tags))
        .all()
    )


# Поиск по ключевым словам в описании
def search_photos_by_keywords(db: Session, keywords: str):
    return (
        db.query(models.Photo).filter(models.Photo.description.contains(keywords)).all()
    )
