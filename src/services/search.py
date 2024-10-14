from sqlalchemy.orm import Session
from src.database.models import Photo
from sqlalchemy import select


async def search_photos(tag: str, keyword: str, db: Session) -> list[Photo]:
    query = db.query(Photo)

    if tag:
        query = query.join(Photo.tags).filter(Photo.tags.any(name=tag))

    if keyword:
        query = query.filter(Photo.description.ilike(f"%{keyword}%"))

    photos = query.all()
    return photos
