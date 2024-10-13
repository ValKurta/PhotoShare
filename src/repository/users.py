from sqlalchemy.orm import Session

from src.database.models import User

from passlib.context import CryptContext
from libgravatar import Gravatar


async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


async def create_user(user_data: dict, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(user_data["email"])
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**user_data, avatar=avatar)
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


async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_user_profile(user: User, update_data: dict, db: Session) -> User:
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
