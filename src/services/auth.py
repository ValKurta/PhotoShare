from typing import Optional
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository.token_blacklist import add_token_to_blacklist

from src.repository import users as repository_users

from src.conf.config import settings

from src.exceptions import CredentialsException, UserBlockedException


class Auth:
    if settings.hashing_scheme == "argon2":
        password_context = CryptContext(
            schemes=["argon2"],
            argon2__time_cost=4,
            argon2__memory_cost=131072,
            argon2__parallelism=4
        )
    else:
        password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    JWT_SECRET_KEY = settings.jwt_secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.password_context.hash(password)

    async def create_token(
            self,
            data: dict,
            expires_delta: Optional[int],
            scope: str,
            default_timedelta: timedelta) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + default_timedelta
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": scope})
        encoded_token = jwt.encode(to_encode, self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_token

    async def create_access_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        return await self.create_token(data, expires_delta, "access_token", timedelta(minutes=30))

    async def create_refresh_token(self, data: dict, expires_delta: Optional[int] = None) -> str:
        return await self.create_token(data, expires_delta, "refresh_token", timedelta(days=7))

    async def decode_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(refresh_token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    def create_email_token(self, data: dict):
        """
        Creates token for email confirmation.

        - **data** (dict): The dict for email token.

        Returns:
        - **str**: email token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.JWT_SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise CredentialsException
            else:
                raise CredentialsException
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise CredentialsException
        elif user.allowed is False:
            raise UserBlockedException
        return user

    async def get_email_from_token(self, token: str):
        """
        Retrieves the email of user by access token.

        :param token: user's token.
        :type token: str
        :return: user's email.
        :rtype: str
        """
        try:
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    async def logout(self, token: str, db: Session) -> None:
        await add_token_to_blacklist(token, db)


auth_service = Auth()
