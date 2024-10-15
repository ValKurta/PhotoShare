from fastapi import HTTPException, status
from src.schemas import RoleEnum
from src.database.models import User


def is_admin(current_user: User):
    """
    This function checks if the given user has administrative privileges.

    Args:
        current_user: The user to check.

    Raises:
        HTTPException: If the user does not have administrative privileges.
    """
    if current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Whoops! Seems that administrative privileges required for this action"
        )


def is_moderator_or_admin(current_user: User):
    """
    This function checks if the given user has moderation or administrative privileges.

    Args:
        current_user: The user to check.

    Raises:
        HTTPException: If the user does not have moderation or administrative privileges.
    """
    if current_user.role != RoleEnum.moderator and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Uh-oh! Only moderators or admins can perform this action"
        )


def is_owner_or_admin(current_user: User, owner_id: int):
    """
    This function checks if the given user is the owner of the item or has administrative privileges.

    Args:
        current_user: The user to check.
        owner_id: The ID of the item's owner.

    Raises:
        HTTPException: If the user is not the owner of the item and does not have administrative privileges.
    """
    if current_user.id != owner_id and current_user.role != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It appears you are not allowed to perform this action"
        )
