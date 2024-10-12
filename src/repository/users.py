from sqlalchemy.orm import Session

from src.database.models import User

from passlib.context import CryptContext
from libgravatar import Gravatar

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
