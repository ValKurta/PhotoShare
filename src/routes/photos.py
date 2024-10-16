from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest

from src.database.db import get_db
from src.repository import photos as repository_photos
from src.schemas import PhotoResponse, PhotoModel, TagsPhoto, TagModel
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User
from src.services.average_rating import get_average_rating

router = APIRouter(prefix="/photos", tags=["photos"])

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

# TODO: fetch all photos of all users


@router.post("/post_photo", response_model=PhotoResponse)
async def create_photo(
    file: UploadFile = File(),
    description: str = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a new photo to Cloudinary and save it in the database.
    Args:
    - **file** (UploadFile): The photo file to be uploaded.
    - **description** (str): Description of the photo.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
    - **PhotoResponse**: The created photo details.
    """
    # Create a clean file identifier
    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    user_name = current_user.username
    public_id = f"PhotoShare/{user_name}{clean_description}{clean_filename}"

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(
            version=r.get("version")
        )

        return await repository_photos.create_photo(description, url, current_user, db)
    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.get("/get_photo/{photo_id}", response_model=PhotoResponse)
async def read_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve details of a photo by its ID.

    Args:
    - **photo_id** (int): ID of the photo.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
    - **PhotoResponse**: The photo details.
    """

    photo = await repository_photos.read_photo(photo_id, current_user, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.put("/update_photo/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    file: UploadFile = File(),
    description: str = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the photo and its description.

    - **photo_id** (int): ID of the photo.
    - **file** (UploadFile): The new photo file to be uploaded.
    - **description** (str): New description for the photo.
    - **db** (Session): Database session dependency.
    - **current_user** (User): The current authenticated user.

    Returns:
    - **PhotoResponse**: The updated photo details.
    """

    # Create a clean file identifier
    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    user_name = current_user.username
    public_id = f"PhotoShare/{user_name}{clean_description}{clean_filename}"

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(
            version=r.get("version")
        )
        photo = await repository_photos.update_photo(
            photo_id, url, description, current_user, db
        )

        if photo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
            )
        return photo

    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.delete("/delete_photo/{photo_id}")
async def delete_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a photo by its ID.

    - **photo_id** (int): The ID of the photo.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **dict**: A confirmation message that the photo was deleted.
    """


    photo = await repository_photos.delete_photo(photo_id, current_user, db)
    return {"photo": photo, "message": "was successfully deleted"}


@router.patch("/add_description/{photo_id}", response_model=PhotoResponse)
async def change_description(
    photo_id: int,
    description: str = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the description of a photo.

    - **photo_id** (int): The ID of the photo.
    - **description** (str): New description for the photo.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the photo is not found.

    Returns:
    - **PhotoResponse**: The updated photo details.
    """

    photo = await repository_photos.change_description(
        photo_id, description, current_user, db
    )
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.get("/get_users_photos/{user_id}", response_model=List[PhotoResponse])
async def get_users_photos(
    user_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve all photos posted by a specific user.

    - **user_id** (int): The ID of the user.
    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: If the user is not found.

    Returns:
    - **List[PhotoResponse]**: List of the user's photos.
    """

    photos = await repository_photos.get_users_photos(user_id, current_user, db)
    if len(photos) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User didn't post any photos"
        )
    return photos


@router.get("/get_my_photos/", response_model=List[PhotoResponse])
async def get_my_photos(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve all photos posted by the current user.

    - **current_user** (User): The current authenticated user.
    - **db** (Session): Database session dependency.

    Returns:
    - **List[PhotoResponse]**: List of the user's photos.
    """


    photos = await repository_photos.get_users_photos(current_user.id, current_user, db)
    if len(photos) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User didn't post any photos"
        )
    return photos

@router.get("/{photo_id}/average-rating")
async def average_rating(photo_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the average rating for a photo.

    - **photo_id** (int): The ID of the photo.
    - **db** (Session): Database session dependency.

    Raises:
    - **HTTPException**: 404 error if the photo is not found or has no ratings.

    Returns:
    - **dict**: A dictionary with the photo ID and its average rating.
        Example:
        ```
        {
            "photo_id": 1,
            "average_rating": 4.3
        }
        ```
    """

    avg_rating = await get_average_rating(db, photo_id)

    if avg_rating is None:
        raise HTTPException(
            status_code=404, detail="Photo not found or no ratings available"
        )

    return {"photo_id": photo_id, "average_rating": avg_rating}

