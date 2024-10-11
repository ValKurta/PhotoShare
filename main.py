import uvicorn
from fastapi import FastAPI
from src.routes import auth
from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.routes import comments

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(comments.router)
app.add_middleware(TokenBlacklistMiddleware)


@app.get("/")
def read_root():
    return {"message": "PhotoShare"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
