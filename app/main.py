from fastapi import FastAPI

from app.api.main_api import main_router
from app.api.user_api import user_router

app: FastAPI = FastAPI(title="CERES API")

app.include_router(main_router)
app.include_router(user_router)
