from typing import Dict

from fastapi import APIRouter

main_router: APIRouter = APIRouter(tags=["main"])

@main_router.get("/")
def root() -> Dict[str, str]:
    return {
        "message": "hello"
    }

