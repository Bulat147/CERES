from typing import List

from fastapi import APIRouter
from fastapi.params import Depends

from app.dependencies.services import get_user_service
from app.dto.user_dto import UserResponse
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/", response_model=List[UserResponse])
def get_users(service: UserService = Depends(get_user_service)) -> List[UserResponse]:
    return service.get_users()
