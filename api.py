from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import Response, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from typing import Annotated
from pathlib import Path

from flashlearn.deps import get_current_user, get_user_handler, ensure_not_logged_in
from flashlearn.utils.user_handler import UserHandler

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path("/interface").resolve()), name="static")
templates = Jinja2Templates(directory=Path("/interface").resolve())

# Token route for user authentication
@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], handler: Annotated[UserHandler, Depends(get_user_handler)], response: Response):
    user = handler.login(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    response.set_cookie(key="access_token", value=f'bearer {user.email}')
    return {"access_token": user.email, "token_type": "bearer"}

# Root page
@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})


# Login page
@app.get("/login")
def login_page(logged_in: Annotated[bool, Depends(ensure_not_logged_in)], request: Request):

    if logged_in:
        return RedirectResponse(url="/home")
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],
          handler: Annotated[UserHandler, Depends(get_user_handler)], 
          logged_in: Annotated[bool, Depends(ensure_not_logged_in)],
          response: Response):
    
    if logged_in:
        return RedirectResponse(url="/home")
    
    user = handler.login(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    response.set_cookie(key="access_token", value=f'bearer {user.email}')
    return RedirectResponse(url="/home")


# Register page
@app.get("/register")
def register_page(logged_in: Annotated[bool, Depends(ensure_not_logged_in)], request: Request):

    if logged_in:
        return RedirectResponse(url="/home")
    
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(form: Annotated[OAuth2PasswordRequestForm, Depends()],
             handler: Annotated[UserHandler, Depends(get_user_handler)], 
             logged_in: Annotated[bool, Depends(ensure_not_logged_in)],
             response: Response):
    
    if logged_in:
        return RedirectResponse(url="/home")
    
    user = handler.register(form.username, form.password, form.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    response.set_cookie(key="access_token", value=f'bearer {user.email}')
    return RedirectResponse(url="/home")


# Home page
@app.get("/home")
def home_page(request: Request, user: Annotated[UserHandler, Depends(get_current_user)]):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

# Logout post
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return RedirectResponse(url="/")


### Run the server ###
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)