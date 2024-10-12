import uvicorn
from fastapi import FastAPI
from src.routes import auth, photos, tags
from src.middleware.security_middleware import TokenBlacklistMiddleware

app = FastAPI()

app.include_router(auth.router)
app.include_router(photos.router)
app.include_router(tags.router)
app.add_middleware(TokenBlacklistMiddleware)


@app.get("/")
def read_root():
    return {"message": "PhotoShare"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

