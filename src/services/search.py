from sqlalchemy.orm import Session
from src.database.models import Photo

async def search_photos(tag: str, keyword: str, db: Session) -> list[Photo]:
    query = db.query(Photo)

    if tag:
        query = query.filter(Photo.tags.any(name=tag))  # Предполагается, что у вас есть связь между Photo и Tag

    if keyword:
        query = query.filter(Photo.description.ilike(f"%{keyword}%"))  # Ищем по описанию

    photos = query.all()
    return photos
