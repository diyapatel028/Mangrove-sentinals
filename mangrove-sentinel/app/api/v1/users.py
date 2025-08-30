from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.base import get_db
from app.database.models import User
from app.database.schemas import User as UserSchema, UserUpdate, UserProfile
from app.auth.dependencies import get_current_active_user
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/leaderboard", response_model=List[UserSchema])
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.is_active == True, User.is_sentinel == True)
        .order_by(User.points.desc())
        .limit(limit)
        .all()
    )
    return users

@router.put("/points")
def award_points(
    points: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    current_user.points += points
    db.commit()
    return {"message": f"Awarded {points} points", "total_points": current_user.points}