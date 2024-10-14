from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import Rating


async def get_average_rating(db: Session, photo_id: int) -> float:
    # Выполняем запрос для вычисления среднего рейтинга фотографии
    avg_rating = (
        db.query(func.avg(Rating.rating)).filter(Rating.photo_id == photo_id).scalar()
    )

    if avg_rating is None:
        return 0.0  # Если нет оценок, возвращаем 0.0
    return round(avg_rating, 2)  # Округляем до 2 знаков
