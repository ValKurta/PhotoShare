from fastapi import HTTPException, status
from src.schemas import RoleEnum
from src.database.models import User


def is_admin(current_user: User):
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Whoops! Seems that administrative privileges required for this action",
        )


def is_moderator_or_admin(current_user: User):
    if current_user.role != RoleEnum.moderator and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Uh-oh! Only moderators or admins can perform this action",
        )


def is_owner_or_admin(current_user: User, owner_id: int):
    if current_user.id != owner_id and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It appears you are not allowed to perform this action",
        )
