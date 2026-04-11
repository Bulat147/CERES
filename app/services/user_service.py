from typing import List

from app.dto.user_dto import UserResponse

class UserService:

    def get_all_users(self) -> List[UserResponse]:
        return [UserResponse(id=1, name="John")]

