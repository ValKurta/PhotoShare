# middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy.exc import IntegrityError

from src.settings import logger


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Do some logging here
    logger.info(f"HTTP Exception: {exc.detail}")
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


async def exception_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except IntegrityError as e:
        logger.debug(e.__class__)
        return JSONResponse(
            content={"message": "Please, specify a correct id"}, status_code=422
        )
    except Exception as e:
        logger.debug(e.__class__)
        # Do some logging here
        logger.warning(f"Unhandled Exception: {str(e)}")
        return JSONResponse(
            content={"message": "Something went wrong"}, status_code=500
        )
