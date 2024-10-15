from sqlalchemy.orm import Session
from src.database.models import Comment
from datetime import datetime

def create_comment(db: Session, photo_id: int, user_id: int, text: str):
    comment = Comment(photo_id=photo_id, user_id=user_id, text=text, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comments(db: Session, photo_id: int):
    return db.query(Comment).filter(Comment.photo_id == photo_id).all()

def update_comment(db: Session, comment_id: int, text: str):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None  
    comment.text = text
    comment.updated_at = datetime.utcnow()  
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment_by_id(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    db.delete(comment)
    db.commit()
    return comment