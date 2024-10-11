import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from src.routes import auth
from fastapi import FastAPI
from src.routes import auth, photos
from src.middleware.security_middleware import TokenBlacklistMiddleware
from src.middleware.rate_limit import RateLimitMiddleware


app = FastAPI()

app.include_router(auth.router)
app.include_router(photos.router)

app.add_middleware(TokenBlacklistMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=10, window_size=60, block_time=60)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 429:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": "Rate limit exceeded, please try again later."},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/")
def read_root():
    return {"message": "PhotoShare"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
