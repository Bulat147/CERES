from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_users(self):
        return self.repo.get_all()

    def get_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def create_user(self, name: str):
        return self.repo.create(name)
