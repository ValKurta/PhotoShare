from sqlalchemy.orm import Session

from src.database.models import User


async def get_user_by_email(email: str, db: Session) -> User:
    # Simulate a user fetch and return a mock user
    if email == "admin@example.com":
        return {"email": email, "hashed_password": "fakepass", "role": "admin"}
    return None
