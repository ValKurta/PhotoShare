from fastapi import APIRouter, Depends

from src.database.models import User
from src.services.auth import auth_service
from src.schemas import UserDbModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDbModel)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve the current authenticated user's details.

    Args:
        current_user (User): The current authenticated user.

    Returns:
        UserDbModel: The current user's details.
    """
    return current_user
