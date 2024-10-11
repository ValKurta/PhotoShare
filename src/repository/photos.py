from typing import List, Type

import sqlalchemy.exc
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Photo, User, Tag
from src.schemas import PhotoModel, PhotoResponse, TagModel, TagsPhoto
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from fastapi import UploadFile, HTTPException, status


async def create_photo(text: str, url: str, db: Session) -> Photo:

    photo = Photo(
        user_id=1,
        url=url,
        description=text
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


async def read_photo(photo_id: int, db: Session) -> Type[Photo] | None:
    return db.query(Photo).filter(Photo.id == photo_id).first()


async def update_photo(photo_id: int, url: UploadFile, description: str, db: Session) -> Photo | None:

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        photo.url = url
        photo.description = description
        db.commit()
    return photo


async def delete_photo(photo_id: int, db: Session) -> Photo | None:

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    print(photo.url)
    if photo:
        db.delete(photo)
        db.commit()
    return photo


async def change_description(photo_id: int, description: str, db: Session) -> Photo | None:

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        photo.description = description
        db.commit()
    return photo


async def add_tags(photo_id: int, body: TagsPhoto, db: Session) -> Photo | None:
    print('REPOSITORY add tags')
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if len(photo.tags) + len(body.tags) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Can assign maximum 5 tags for a photo, '
                                   f'Existing tags: {[tag.name for tag in photo.tags]}')
    print('REPOSITORY add tags b4 try')
    # Appends tags one by one to the photo
    for tag in body.tags:
        await add_tag(photo_id, tag, db)
    # try:
    #     for tag in body.tags:
    #         await check_unique_tags(photo, tag)
    #
    #         if check_existing_tag(tag, db):
    #             photo.tags.append(tag)
    #         else:
    #             new_tag = Tag(name=tag)
    #             photo.tags.append(new_tag)
    #     db.commit()
    # except sqlalchemy.exc.DatabaseError as e:
    #     print(e)
    return photo


async def add_tag(photo_id: int, tag: str, db: Session) -> Type[Photo] | None:
    print('Repository ADD TAG')
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

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


async def remove_tags(photo_id: int, db: Session) -> Photo | None:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()

    if photo:
        photo.tags = []
        db.commit()
    return photo


async def remove_tag(photo_id: int, tag: str, db: Session) -> Type[Photo] | None:
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    db_tag = db.query(Tag).filter(Tag.name == tag).first()

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
