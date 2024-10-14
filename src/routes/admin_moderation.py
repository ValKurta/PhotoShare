from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest

from src.routes.permissions import is_admin
from src.database.db import get_db
from src.repository import admin_moderation as repository_admin_moderation
from src.schemas import Comment, PhotoResponse, PhotoModel, TagsPhoto, UserStatistics
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User, Comment as DB_Comment

router = APIRouter(prefix="/admin", tags=["admin_moderation"])

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


def create_public_id(description: str, file: UploadFile) -> tuple[str, str, str]:
    """Create a clean file identifier and return clean description, clean filename and public id."""

    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    public_id = f"PhotoShare/{clean_description}{clean_filename}"

    return public_id


@router.get("/statistics", response_model=List[UserStatistics])
async def get_user_statistics(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # raise ValueError("Not implemented")
    is_admin(current_user)

    return await repository_admin_moderation.get_user_statistics(db)


@router.post("/add_photo", response_model=PhotoResponse)
async def create_photo(
    file: UploadFile = File(),
    description: str = Form(),
    user_id: int = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Check if the current user is an admin
    is_admin(current_user)

    # Create a clean file identifier
    public_id = create_public_id(description, file)

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(
            crop="fill", version=r.get("version")
        )

        return await repository_admin_moderation.create_photo(
            user_id, description, url, db
        )
    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.get("/get-photo/{photo_id}", response_model=PhotoResponse)
async def read_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Check if the current user is an admin
    is_admin(current_user)

    photo = await repository_admin_moderation.read_photo(photo_id, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.put("/update-photo/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: int,
    file: UploadFile = File(),
    description: str = Form(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Check if the current user is an admin
    is_admin(current_user)

    public_id = create_public_id(description, file)

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(
            crop="fill", version=r.get("version")
        )

        photo = await repository_admin_moderation.update_photo(
            photo_id, url, description, db
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


@router.delete("/delete-photo/{photo_id}", response_model=PhotoResponse)
async def delete_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Check if the current user is an admin
    is_admin(current_user)

    photo = await repository_admin_moderation.delete_photo(photo_id, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.patch("/patch-photo/{photo_id}", response_model=PhotoResponse)
async def change_description(
    photo_id: int,
    description: str,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    # Check if the current user is an admin
    is_admin(current_user)

    photo = await repository_admin_moderation.change_description(
        photo_id, description, db
    )
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.patch("/add_tags/{photo_id}", response_model=PhotoResponse)
async def add_tags(
    photo_id: int,
    body: TagsPhoto,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    if len(body.tags) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can assign maximum 5 tags for a photo",
        )

    photo = await repository_admin_moderation.add_tags(photo_id, body, db)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )
    return photo


@router.delete("/delete-comment/{comment_id}", response_model=Comment)
async def remove_comment(
    comment_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    is_admin(current_user)

    deleted_comment = db.query(DB_Comment).filter(DB_Comment.id == comment_id).first()

    if not deleted_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(deleted_comment)
    db.commit()

    return Comment(
        id=deleted_comment.id,
        text=deleted_comment.text,
        created_at=deleted_comment.created_at.isoformat(),
        updated_at=deleted_comment.updated_at.isoformat(),
        user_id=deleted_comment.user_id,
        photo_id=deleted_comment.photo_id,
    )
