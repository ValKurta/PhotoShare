import os
import redis
import uvicorn

from fastapi import FastAPI, Request, Depends

from src.routes import auth
from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.routes import auth, admin_moderation, photos, tags, comments

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from src.routes import (
    auth,
    admin_moderation,
    photos,
    rating,
    search,
    filter,
    average_rating,
)
from src.middleware.security_middleware import TokenBlacklistMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.conf.config import settings
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from contextlib import asynccontextmanager
import redis.asyncio as aioredis

from src.middleware.exception_handlers import (
    http_exception_handler,
    exception_handling_middleware,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await aioredis.from_url(
        f"redis://{settings.redis_host}:{settings.redis_port}",
        encoding="utf-8",
        decode_responses=True
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


app = FastAPI(
    lifespan=lifespan, dependencies=[Depends(RateLimiter(times=2, seconds=5))]
)

app.include_router(auth.router)
app.include_router(filter.router)
app.include_router(photos.router)
app.include_router(tags.router)
app.include_router(admin_moderation.router)
app.include_router(rating.router)
app.include_router(search.router)
app.include_router(average_rating.router)
app.include_router(comments.router)

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
