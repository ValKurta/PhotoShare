from sqlalchemy.orm import Session
from src.database.models import BlacklistedToken


async def is_token_blacklisted(jti: str, db: Session) -> bool:
    token = db.query(BlacklistedToken).filter(BlacklistedToken.jwt == jti).first()
    return token is not None

async def add_token_to_blacklist(jti: str, db: Session) -> None:
    blacklisted_token = BlacklistedToken(jwt=jwt)
    db.add(blacklisted_token)
    db.commit()
