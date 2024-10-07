from fastapi import FastAPI
from src.routes import auth


app = FastAPI()

app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"PhotoShare"}

