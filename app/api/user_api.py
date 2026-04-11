from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from app.dto.user_dto import UserResponse
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/", response_model=List[UserResponse])
def get_users(service: UserService = Depends()) -> List[UserResponse]:
    return service.get_all_users()
