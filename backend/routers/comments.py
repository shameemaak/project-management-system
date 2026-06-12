from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Comment, User
from schemas.comment import CommentCreate, CommentResponse
from auth.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse)
def create_comment(comment_data: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = Comment(
        content=comment_data.content,
        task_id=comment_data.task_id,
        user_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/task/{task_id}", response_model=list[CommentResponse])
def get_comments(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Comment).filter(Comment.task_id == task_id).all()

@router.delete("/{comment_id}")
def delete_comment(comment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}
