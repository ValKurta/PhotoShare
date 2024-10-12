import uvicorn
from fastapi import FastAPI
<<<<<<< HEAD
from src.routes import auth
from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.routes import comments

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(comments.router)
=======
from src.routes import admin_moderation
from src.routes import auth, photos
from src.middleware.security_middleware import TokenBlacklistMiddleware

app = FastAPI()

app.include_router(auth.router)
app.include_router(photos.router)
app.include_router(admin_moderation.router)

>>>>>>> origin/develop
app.add_middleware(TokenBlacklistMiddleware)


@app.get("/")
def read_root():
    return {"message": "PhotoShare"}


if __name__ == "__main__":
<<<<<<< HEAD
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
=======
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

>>>>>>> origin/develop
