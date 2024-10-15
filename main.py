import os
import redis.asyncio as aioredis
import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from contextlib import asynccontextmanager
from starlette.exceptions import HTTPException as StarletteHTTPException


from src.routes import (
    auth,
    admin_moderation,
    photos,
    rating,
    search,
    filter,
    tags,
    comments,
    users,
    photo_transformation
)

from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.middleware.exception_handlers import (
    http_exception_handler,
    exception_handling_middleware,
)
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf-8",
        decode_responses=True,
    )

    try:
        await redis.ping()
        print("Connected to Redis successfully!")
        await FastAPILimiter.init(redis)
        print("FastAPILimiter initialized successfully!")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

    yield

    await redis.close()
    print("Application is shutting down")


description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

description = """
## Welcome to PhotoShare API!

This API allows you to upload, manage, and rate photos. You can also manage users, photos, and tags.

### Features:
- **User accounts**: Sign up, log in, and manage user roles;
- **Photo management**: Upload and manage photos (Cloudinary); 
- **Rating system**: Rate and get average ratings of photos.
- **Comment system**: Create and manage comments for every photo.  
    """

app = FastAPI(
    title="PhotoShare RestAPI",
    description=description,
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
    docs_url="/docs",
    redoc_url=None,
)

app.include_router(auth.router)
app.include_router(filter.router)
app.include_router(photos.router)
app.include_router(photo_transformation.router)
app.include_router(tags.router)
app.include_router(admin_moderation.router)
app.include_router(rating.router)
app.include_router(search.router)
# app.include_router(average_rating.router)
app.include_router(comments.router)
app.include_router(users.router)

app.add_middleware(TokenBlacklistMiddleware)


origins = [
    "http://localhost:3000",  # FrontEnd
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "PhotoShare"}


# Register the exception handler
app.add_exception_handler(StarletteHTTPException, http_exception_handler)


# Register the middleware
@app.middleware("http")
async def exception_handling_middleware_app(request: Request, call_next):
    return await exception_handling_middleware(request, call_next)


if __name__ == "__main__":
    reload_flag = True
    if settings.use_https:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        keyfile_path = os.path.join(base_dir, "key.pem")
        certfile_path = os.path.join(base_dir, "cert.pem")

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=keyfile_path,
            ssl_certfile=certfile_path,
            reload=reload_flag,
        )
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload_flag)
