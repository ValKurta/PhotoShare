from typing import List, Type

from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from src.schemas import PhotoModel, PhotoResponse, TagModel, TagsPhoto


from fastapi import UploadFile, HTTPException, status


async def add_tags(photo_id: int, body: TagsPhoto, user: User, db: Session) -> Photo | None:
    print('REPOSITORY add tags')
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()

    if len(photo.tags) + len(body.tags) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Can assign maximum 5 tags for a photo, '
                                   f'Existing tags: {[tag.name for tag in photo.tags]}')
    print('REPOSITORY add tags b4 try')
    # Appends tags one by one to the photo
    for tag in body.tags:
        await add_tag(photo_id, tag, user, db)
    return photo


async def add_tag(photo_id: int, tag: str, user: User, db: Session) -> Type[Photo] | None:
    print('Repository ADD TAG')
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()

    if not photo:
        return None

    # Check existing quantity of tags in photo
    if len(photo.tags) >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Can assign maximum 5 tags for a photo, '
                                   f'Photo tags: {[tag.name for tag in photo.tags]}')

    # Check that tags are unique for photo
    await check_unique_tags(photo, tag)

    # Check if tag already exist in DB
    existing_tag = db.query(Tag).filter(Tag.name == tag).first()
    if existing_tag:
        photo.tags.append(existing_tag)
    else:
        new_tag = Tag(name=tag)
        photo.tags.append(new_tag)
    db.commit()
    return photo


async def remove_tags(photo_id: int, user: User, db: Session) -> Photo | None:
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()

    if photo:
        photo.tags = []
        db.commit()
    return photo


async def remove_tag(photo_id: int, tag: str, user: User, db: Session) -> Type[Photo] | None:
    photo = db.query(Photo).filter(and_(Photo.id == photo_id, Photo.user_id == user.id)).first()
    db_tag = db.query(Tag).filter(and_(Tag.name == tag, Photo.user_id == user.id)).first()

    # Check if photo exists
    if photo and db_tag:
        # Check if photo contain required tag and removes it
        if db_tag.name in [ex_tag.name for ex_tag in photo.tags]:
            photo.tags.remove(db_tag)
            db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"The photo doesn't contain a tag '{db_tag.name}'")
    else:
        return None
    return photo


async def check_unique_tags(photo: Type[Photo], tag: str):
    for tag_obj in photo.tags:
        if tag_obj.name == tag:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Tags should be unique. Photos tags: {[tag.name for tag in photo.tags]}')


async def search_photos(tag: str, db: Session) -> list[Type[Photo]]:
    photos = db.query(Photo).join(Photo.tags).filter(Tag.name == tag).all()
    return photos
