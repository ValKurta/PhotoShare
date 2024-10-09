from fastapi import FastAPI
from src.routes import auth
from src.middleware.security_middleware import TokenBlacklistMiddleware


app = FastAPI()

app.include_router(auth.router)
app.add_middleware(TokenBlacklistMiddleware)


@app.get("/")
def read_root():
    return {"PhotoShare"}
