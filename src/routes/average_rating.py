from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.average_rating import get_average_rating

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}/average-rating")
async def average_rating(photo_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the average rating for a photo.

    Args:
        photo_id (int): The ID of the photo.
        db (Session, optional): Dependency for database connection. Defaults to get_db.

    Raises:
        HTTPException: 404 error if the photo is not found or has no ratings.

    Returns:
        dict: A dictionary with the photo ID and its average rating.
        Example:
        {
            "photo_id": 1,
            "average_rating": 4.3
        }
    """

    avg_rating = await get_average_rating(db, photo_id)

    if avg_rating is None:
        raise HTTPException(
            status_code=404, detail="Photo not found or no ratings available"
        )

    return {"photo_id": photo_id, "average_rating": avg_rating}
