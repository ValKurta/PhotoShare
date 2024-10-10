from sqlalchemy.orm import Session
from typing import Type

from src.database.models import User
# from src.schemas import UserCreateModel


async def get_user_by_email(email: str, db: Session) -> Type[User] | None:
    return db.query(User).filter(User.email == email).first()
    # Simulate a user fetch and return a mock user
    # if email == "admin@example.com":
    #     return {"email": email, "hashed_password": "fakepass", "role": "admin"}
    # return None
