from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import tags as repository_tags
from src.schemas import PhotoResponse, PhotoModel, TagsPhoto, TagModel
from src.services.auth import auth_service


router = APIRouter(prefix="/tags", tags=["tags"])


@router.patch("/add_tags/{photo_id}", response_model=PhotoResponse)
async def add_tags(
    photo_id: int,
    body: TagsPhoto,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add multiple tags to a photo (max 5).

    - **photo_id** (int): The ID of the photo to update.
    - **body** (TagsPhoto): The tags to add.
    - **db** (Session): Database session dependency.
    - **current_user** (User): The current authenticated user.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **PhotoResponse**: The updated photo details.
    """

    photo = await repository_tags.add_tags(photo_id, body, current_user, db)

    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.delete("/remove_tags/{photo_id}", response_model=PhotoResponse)
async def remove_tags(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove all tags from a photo.

    - **photo_id** (int): The ID of the photo to update.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **PhotoResponse**: The updated photo details.
    """

    photo = await repository_tags.remove_tags(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.patch("/add_tag/{photo_id}", response_model=PhotoResponse)
async def add_tag(
    photo_id: int,
    tag: str = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a single tag to a photo.

    - **photo_id** (int): The ID of the photo to update.
    - **tag** (str): The tag to add.
    - **db** (Session): Database session dependency.
    - **current_user** (User): The current authenticated user.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **PhotoResponse**: The updated photo details.
    """

    photo = await repository_tags.add_tag(photo_id, tag, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.delete("/remove_tag/{photo_id}", response_model=PhotoResponse)
async def remove_tag(
    photo_id: int,
    tag: str = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a single tag from a photo.

    - **photo_id** (int): The ID of the photo to update.
    - **tag** (str): The tag to remove.
    - **db** (Session): Database session dependency.
    - **current_user** (User): The current authenticated user.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **PhotoResponse**: The updated photo details.
    """

    photo = await repository_tags.remove_tag(photo_id, tag, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/search_photos/by_tag", response_model=List[PhotoResponse])
async def search_photos_by_tag(tag: str, db: Session = Depends(get_db)):
    """
    Search for photos by tag.

    - **tag** (str): The tag to search for.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If no photos are found.

    Returns:
    - **List[PhotoResponse]**: A list of photos with the specified tag.
    """

    photos = await repository_tags.search_photos(tag, db)
    print(photos)
    if photos is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photos not found"
        )
    return photos
