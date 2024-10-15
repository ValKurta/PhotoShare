from src.settings import logger
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import Rating, User


async def get_average_rating(db: Session, photo_id: int) -> float:
    # query to calculate average value
    avg_rating = (
        db.query(func.avg(Rating.rating)).filter(Rating.photo_id == photo_id).scalar()
    )

    if avg_rating is None:
        return 0.0  # default
    return round(avg_rating, 2)  # 2.2 for instance


async def get_average_rating_user_gives(db: Session, user_id: int) -> float:
    # query to calculate average value
    avg_rating = (
        db.query(func.avg(Rating.rating)).filter(Rating.user_id == user_id).scalar()
    )

    if avg_rating is None:
        return 0.0  # default
    return round(avg_rating, 2)


async def get_user_rating(db: Session, user_id: int) -> float:
    # query to calculate average value
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    avg_ratings = [
        await get_average_rating(db, photo.id) for photo in user.photos if photo.ratings
    ]
    logger.debug(user.photos)
    logger.debug(avg_ratings)
    return round(sum(avg_ratings) / len(avg_ratings), 2) if avg_ratings else 0.0

