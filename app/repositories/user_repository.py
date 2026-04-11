from sqlalchemy.orm import Session
from app.models.user_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, name: str) -> User:
        user = User(name=name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
