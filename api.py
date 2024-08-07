from fastapi import FastAPI, Depends, Request
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from typing import Annotated
from pathlib import Path

from flashlearn.deps import get_current_user

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path("/interface").resolve()), name="static")
templates = Jinja2Templates(directory=Path("/interface").resolve())

# Token route for login functionality
@app.post("/token")
# user_manager to be obtained through dep injection (Depends())
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], user_manager, response: Response):
    ### Change with how user_manager is defined
    user = user_manager.login(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    response.set_cookie(key="access_token", value=f'bearer {form.username}')
    return {"access_token": form.username, "token_type": "bearer"}

# Root page
@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})

### Run the server ###
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)