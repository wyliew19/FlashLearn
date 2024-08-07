from fastapi import HTTPException, Depends
from flashlearn.security.cookie import OAuth2WithCookie
from flashlearn.adts.user import User
from flashlearn.utils.user_handler import UserHandler
from fastapi.responses import RedirectResponse

from typing import Annotated

oauth2_scheme = OAuth2WithCookie(tokenUrl="/token")

def get_current_user(email: Annotated[str, Depends(oauth2_scheme)]) -> User:
    handler = UserHandler()
    user = handler.get_user(email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    return user

def ensure_not_logged_in(email: Annotated[str, Depends(oauth2_scheme)]):
    handler = UserHandler()
    user = handler.get_user(email)
    if user is not None:
        # Redirect to the home page
        return True
    return False

def get_user_handler():
    return UserHandler()
