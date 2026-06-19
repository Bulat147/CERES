from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def get_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    if token is None:
        return None
    return token.credentials