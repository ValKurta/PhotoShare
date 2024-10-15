import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.services.rating import add_rating
from src.schemas import RatingCreate
from src.database.models import Photo, User, Rating
from src.repository.photos import create_photo
from fastapi import HTTPException, status, Depends


@pytest.mark.asyncio
async def test_add_rating_success():
    db = MagicMock(spec=Session)
    mock_photo = Photo(id=1, user_id=2)
    db.query().filter().first.side_effect = [mock_photo, None]  # Photo exists, no existing rating

    rating_data = RatingCreate(rating=4)

    result = await add_rating(db=db, photo_id=1, rating=rating_data, user_id=3)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

    assert isinstance(result, Rating)
    assert result.photo_id == 1
    assert result.user_id == 3
    assert result.rating == 4

@pytest.mark.asyncio
async def test_add_rating_photo_not_found():
    db = MagicMock(spec=Session)
    db.query().filter().first.side_effect = [None]
    rating_data = RatingCreate(rating=4)

    with pytest.raises(HTTPException) as exc_info:
        await add_rating(db=db, photo_id=1, rating=rating_data, user_id=3)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Photo not found"

@pytest.mark.asyncio
async def test_add_rating_owner_cannot_rate_own_photo():
    db = MagicMock(spec=Session)
    mock_photo = Photo(id=1, user_id=3)
    db.query().filter().first.side_effect = [mock_photo]

    rating_data = RatingCreate(rating=4)

    with pytest.raises(HTTPException) as exc_info:
        await add_rating(db=db, photo_id=1, rating=rating_data, user_id=3)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You are the photo's owner! Rate a photo of other people"

@pytest.mark.parametrize("invalid_rating", [0, 6])
@pytest.mark.asyncio
async def test_add_rating_invalid_rating_range(invalid_rating):
    db = MagicMock(spec=Session)
    mock_photo = Photo(id=1, user_id=2)
    db.query().filter().first.side_effect = [mock_photo, None]

    rating_data = RatingCreate(rating=invalid_rating)

    with pytest.raises(HTTPException) as exc_info:
        await add_rating(db=db, photo_id=1, rating=rating_data, user_id=3)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Rating can be between 1 and 5"

@pytest.mark.asyncio
async def test_add_rating_already_rated():
    db = MagicMock(spec=Session)
    mock_photo = Photo(id=1, user_id=2)
    mock_existing_rating = Rating(photo_id=1, user_id=3, rating=4)
    db.query().filter().first.side_effect = [mock_photo, mock_existing_rating]

    rating_data = RatingCreate(rating=4)

    with pytest.raises(HTTPException) as exc_info:
        await add_rating(db=db, photo_id=1, rating=rating_data, user_id=3)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "You have rated this photo already!"