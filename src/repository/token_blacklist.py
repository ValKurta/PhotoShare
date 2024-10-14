from sqlalchemy.orm import Session
from src.database.models import BlacklistedToken


async def is_token_blacklisted(token: str, db: Session) -> bool:
    token = db.query(BlacklistedToken).filter(BlacklistedToken.jwt == token).first()
    return token is not None


async def add_token_to_blacklist(token: str, db: Session) -> None:
    blacklisted_token = BlacklistedToken(jwt=token)
    db.add(blacklisted_token)
    db.commit()
