from sqlalchemy.orm import Session
from typing import Type

from src.database.models import User
from src.schemas import UserCreateModel, RoleEnum
from fastapi import HTTPException
from passlib.context import CryptContext
from libgravatar import Gravatar


async def get_user_by_email(email: str, db: Session) -> Type[User] | None:
    return db.query(User).filter(User.email == email).first()


async def create_user(user: UserCreateModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(user.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**user.dict(exclude_unset=True), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def get_user_count(db: Session):
    return db.query(User).count()


async def get_user_by_id(user_id: int, db: Session):
    return db.query(User).filter(User.id == user_id).first()


async def update_user_in_db(user: User, db: Session):
    db.add(user)
    db.commit()
    db.refresh(user)
