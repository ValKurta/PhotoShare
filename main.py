import os
import redis
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from src.routes import auth
from fastapi import FastAPI, Depends
from src.routes import auth, photos
from src.middleware.security_middleware import TokenBlacklistMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.conf.config import settings
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


app = FastAPI()

app.include_router(auth.router)
app.include_router(photos.router)

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

@app.on_event("startup")
async def startup():
    r = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        r.ping()
        print("Connected to Redis successfully!")
        await FastAPILimiter.init(r)
    except redis.ConnectionError:
        print("Failed to connect to Redis!")


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_root():
    return {"message": "PhotoShare"}


if __name__ == "__main__":

    if settings.use_https:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        keyfile_path = os.path.join(base_dir, "key.pem")
        certfile_path = os.path.join(base_dir, "cert.pem")

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            ssl_keyfile=keyfile_path,
            ssl_certfile=certfile_path,
        )
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000)
