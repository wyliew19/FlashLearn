from fastapi import HTTPException
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request

# Thank you to https://github.com/tiangolo/fastapi/issues/796#issuecomment-566243767
# for the idea to subclass OAuth2 and add a cookie parameter

class OAuth2WithCookie(OAuth2):
    def __init__(self, tokenUrl: str, scheme_name: str = None, scopes: dict = None, auto_error: bool = True):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(
            password={
                "tokenUrl": tokenUrl,
                "scopes": scopes,
            }
        )
        super().__init__(scheme_name=scheme_name, flows=flows, auto_error=auto_error)

    async def __call__(self, request: Request):
        authorization: str = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(status_code=302, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer", "Location": "/login"})
            return None
        return param
