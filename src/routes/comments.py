# src/routes/comments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository.comments import create_comment, get_comments, update_comment, delete_comment
from src.schemas import CommentCreate, CommentUpdate,  Comment, CommentBase
from typing import List

router = APIRouter()

@router.post("/comments/", response_model=Comment)
def add_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return create_comment(db, comment.photo_id, comment.user_id, comment.text)

@router.get("/comments/{photo_id}", response_model=List[Comment])
def read_comments(photo_id: int, db: Session = Depends(get_db)):
    comments = get_comments(db, photo_id)
    return comments

@router.put("/comments/{comment_id}")
async def modify_comment(comment_id: int, comment: CommentUpdate, user_id: int, db: Session = Depends(get_db)):
    user = await get_user_by_id(user_id, db)  # Отримай користувача за ID

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if existing_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Перевірка, чи користувач є автором коментаря
    if existing_comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this comment")

    # Оновлення коментаря
    for key, value in comment.dict(exclude_unset=True).items():
        setattr(existing_comment, key, value)

    db.commit()
    db.refresh(existing_comment)
    
    return existing_comment

@router.delete("/comments/{comment_id}", response_model=Comment)
async def remove_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    # Отримай користувача за ID
    user = await get_user_by_id(user_id, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Перевірка, чи користувач є адміністратором або модератором
    if user.role not in ["admin", "moderator"]:  
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    deleted_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not deleted_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(deleted_comment)
    db.commit()
    
    return deleted_comment



