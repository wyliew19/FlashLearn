from fastapi import HTTPException, Depends
from flashlearn.security.cookie import OAuth2WithCookie

from typing import Annotated

oauth2_scheme = OAuth2WithCookie(tokenUrl="/token")

# TODO: Implement making database handling to return User object
def get_current_user(email: Annotated[str, Depends(oauth2_scheme)]) -> User:
    pass
