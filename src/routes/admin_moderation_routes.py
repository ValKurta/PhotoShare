# to check if user is admin
from fastapi import APIRouter, Depends
from src.services.auth import get_current_user
from src.repository.token_blacklist import add_token_to_blacklist

router = APIRouter()


# Simply, when the user is admin, do everything you do in CRUD for a single usir, but for all users