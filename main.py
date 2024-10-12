import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from src.routes import auth
from fastapi import FastAPI, Depends
from src.routes import auth, photos
from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.conf.config import settings

app = FastAPI()

app.include_router(auth.router)
app.include_router(photos.router)

app.add_middleware(TokenBlacklistMiddleware)


@app.get("/")
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
