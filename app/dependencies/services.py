from sqlalchemy.orm import Session
from fastapi import Depends

from app.dependencies.db import get_db
from app.services.user_service import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
