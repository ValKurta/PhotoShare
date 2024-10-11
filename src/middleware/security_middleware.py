from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi import HTTPException, status
from jose import JWTError, jwt
from src.database.models import BlacklistedToken
from src.database.db import get_db
from src.conf.config import settings


class TokenBlacklistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.jwt_secret_key = settings.jwt_secret_key
        self.algorithm = settings.algorithm

    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get("Authorization")

        if authorization:
            token_type, token = authorization.split()

            if token_type.lower() == "bearer":
                try:
                    payload = jwt.decode(
                        token, self.jwt_secret_key, algorithms=[self.algorithm]
                    )
                    token_id = payload.get("jti")
                    print(token_id)
                    db = next(get_db())
                    blacklisted_token = (
                        db.query(BlacklistedToken).filter_by(jwt=token).first()
                    )

                    if blacklisted_token:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token is blacklisted. Please log in again.",
                        )
                except JWTError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                    )
        response = await call_next(request)
        return response
