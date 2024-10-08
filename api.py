from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import Response, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from typing import Annotated
from pathlib import Path

from flashlearn.deps import get_current_user, get_user_handler, ensure_not_logged_in, get_set_handler
from flashlearn.utils.user_handler import UserHandler
from flashlearn.utils.set_handler import SetHandler
from flashlearn.utils.database import DatabaseManager
from flashlearn.models.user import User

app = FastAPI()
app.mount("/assets", StaticFiles(directory=Path("./interface/assets").resolve()), name="assets")
templates = Jinja2Templates(directory=Path("./interface").resolve())

# Ensure database is created
DatabaseManager()

# Token route for user authentication
@app.post("/token")
def login_token(form: Annotated[OAuth2PasswordRequestForm, Depends()], handler: Annotated[UserHandler, Depends(get_user_handler)], response: Response):
    user = handler.login(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    response.set_cookie(key="access_token", value=f'bearer {user.email}')
    return {"access_token": user.email, "token_type": "bearer"}

# Root page
@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = "favicon.ico"
    return FileResponse(Path(f"./interface/assets/{file_name}"), headers={"Content-Disposition": "attachment; filename=" + file_name})


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
    return {"access_token": user.email, "token_type": "bearer"}


# Register page
@app.get("/register")
def register_page(logged_in: Annotated[bool, Depends(ensure_not_logged_in)], request: Request):

    if logged_in:
        return RedirectResponse(url="/home")
    
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(handler: Annotated[UserHandler, Depends(get_user_handler)], 
             logged_in: Annotated[bool, Depends(ensure_not_logged_in)],
             response: Response, username: str = Form(), password: str = Form(), 
             email: str = Form()):
    
    if logged_in:
        return RedirectResponse(url="/home")
    
    user = handler.register(username, password, email)
    # If user is None, registration failed
    if user is None:
        raise HTTPException(status_code=500, detail="Failed to register user")
    response.set_cookie(key="access_token", value=f'bearer {user.email}')
    return {"access_token": user.email, "token_type": "bearer"}


# Home page
@app.get("/home")
def home_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.post("/home")
def home_page_post(request: Request, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

# Logout
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    return response

# Profile page
@app.get("/profile")
def profile_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.post("/profile")
def profile_page_post(request: Request, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.post("/new_password")
def new_password(current_password: str, password: str, 
                 user: Annotated[User, Depends(get_current_user)], 
                 handler: Annotated[UserHandler, Depends(get_user_handler)]):
    if not handler.login(user.email, current_password):
        raise HTTPException(status_code=401, detail="Invalid current password")
    handler.change_password(user.email, password)
    return RedirectResponse(url="/profile")

# Get user sets
@app.get("/sets")
def get_sets(request: Request, user: Annotated[User, Depends(get_current_user)], 
             handler: Annotated[SetHandler, Depends(get_set_handler)]):
    sets = handler.get_user_sets(user.id)
    return templates.TemplateResponse("sets.html", {"request": request, "sets": sets, "user": user})

@app.post("/sets")
def get_sets_post(request: Request, user: Annotated[User, Depends(get_current_user)],
                    handler: Annotated[SetHandler, Depends(get_set_handler)]):
        sets = handler.get_user_sets(user.id)
        return templates.TemplateResponse("sets.html", {"request": request, "sets": sets, "user": user})

# Get set
@app.get("/set/{set_id}")
def get_set(request: Request, set_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    set = handler.get_set(set_id)
    return templates.TemplateResponse("set.html", {"request": request, "set": set, "user": user})

@app.post("/set/{set_id}")
def get_set_post(request: Request, set_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    set = handler.get_set(set_id)
    return templates.TemplateResponse("set.html", {"request": request, "set": set, "user": user})

# Get super set
@app.get("/super_set/{super_id}")
def get_super_set(request: Request, super_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    super_set = handler.get_super_set(super_id)
    return templates.TemplateResponse("super_set.html", {"request": request, "super_set": super_set, "user": user})

@app.post("/super_set/{super_id}")
def get_super_set_post(request: Request, super_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    super_set = handler.get_super_set(super_id)
    return templates.TemplateResponse("super_set.html", {"request": request, "super_set": super_set, "user": user})

# Create set
@app.get("/create_set")
def create_set_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("create_set.html", {"request": request, "user": user})

@app.post("/create_set")
def create_set(user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)],
                name: str = Form()):
    handler.create_set(name, user.id)
    return RedirectResponse(url="/sets")

# Subset creation
@app.get("/create_set/{super_id}")
def create_set_page(request: Request, super_id: int, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("create_set.html", {"request": request, "user": user, "super_id": super_id})

@app.post("/create_set/{super_id}")
def create_set(super_id: int, user: Annotated[User, Depends(get_current_user)], 
                handler: Annotated[SetHandler, Depends(get_set_handler)], name: str = Form()):
    handler.create_set(name, user.id, super_id)
    return RedirectResponse(url=f"/super_set/{super_id}")

# Create super set
@app.get("/create_super_set")
def create_super_set_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("create_super_set.html", {"request": request, "user": user})

@app.post("/create_super_set")
def create_super_set(user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)],
                     name: str = Form()):
    handler.create_super_set(name, user.id)
    return RedirectResponse(url="/sets")

# Create flashcard
@app.get("/create_flashcard/{set_id}")
def create_flashcard_page(request: Request, set_id: int, user: Annotated[User, Depends(get_current_user)]):
    return templates.TemplateResponse("create_flashcard.html", {"request": request, "user": user, "set_id": set_id})

@app.post("/create_flashcard/{set_id}")
def create_flashcard(set_id: int, term: Annotated[str, Form()], body: Annotated[str, Form()],
                     user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    # Create flashcard
    handler.add_card_to_set(set_id, user.email, term, body)
    return RedirectResponse(url=f"/set/{set_id}")

# Edit set
@app.get("/edit_set/{set_id}")
def edit_set_page(request: Request, set_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    set = handler.get_set(set_id)
    return templates.TemplateResponse("edit_set.html", {"request": request, "user": user, "set": set})

@app.post("/edit_set/{set_id}")
def edit_set(set_id: int, handler: Annotated[SetHandler, Depends(get_set_handler)], name: str = Form()):
    handler.edit_set(set_id, name)
    return RedirectResponse(url=f"/set/{set_id}")

# Delete set
@app.get("/delete_set/{set_id}")
def delete_set_page(request: Request, set_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    handler.delete_set(set_id)
    return RedirectResponse(url="/sets")

# Delete super set
@app.get("/delete_super_set/{super_id}")
def delete_super_set_page(request: Request, super_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    handler.delete_super_set(super_id)
    return RedirectResponse(url="/sets")

# Edit super set
@app.get("/edit_super_set/{super_id}")
def edit_super_set_page(request: Request, super_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    super_set = handler.get_super_set(super_id)
    return templates.TemplateResponse("edit_super_set.html", {"request": request, "user": user, "super_set": super_set})

@app.post("/edit_super_set/{super_id}")
def edit_super_set(super_id: int, handler: Annotated[SetHandler, Depends(get_set_handler)], name: str = Form()):
    handler.edit_super_set(super_id, name)
    return RedirectResponse(url=f"/super_set/{super_id}")

# Edit flashcard
@app.get("/edit_flashcard/{card_id}")
def edit_flashcard_page(request: Request, card_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    card = handler.get_card(card_id)
    return templates.TemplateResponse("edit_flashcard.html", {"request": request, "user": user, "card": card})

@app.post("/edit_flashcard/{card_id}")
def edit_flashcard(card_id: int, handler: Annotated[SetHandler, Depends(get_set_handler)],
                   term: Annotated[str | None, Form()], body: Annotated[str | None, Form()]):
    card = handler.edit_card(card_id, term, body)
    return RedirectResponse(url=f"/set/{card.set_id}")

# Delete flashcard
@app.get("/delete_flashcard/{card_id}")
def delete_flashcard_page(request: Request, card_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    set_id = handler.get_card(card_id).set_id
    handler.delete_card(card_id)
    return RedirectResponse(url=f"/set/{set_id}")

# Study mode
@app.get("/study/new_session/{set_id}")
def new_study_session(request: Request, set_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    card = handler.get_next_unstudied_card(set_id=set_id)
    if card is None:
        return RedirectResponse(url="/sets")
    return RedirectResponse(url=f"/study/{card.id}")

@app.get("/study/{card_id}")
def study_page(request: Request, card_id: int, user: Annotated[User, Depends(get_current_user)], handler: Annotated[SetHandler, Depends(get_set_handler)]):
    card = handler.get_card(card_id)
    return templates.TemplateResponse("study.html", {"request": request, "user": user, "card": card})

@app.get("/study/studied/{card_id}")
def mark_card_as_studied(card_id: int, handler: Annotated[SetHandler, Depends(get_set_handler)]):
    card = handler.study_card(card_id)
    return RedirectResponse(url=f"/study/new_card/{card.id}")

@app.get("/study/new_card/{card_id}")
def get_next_unstudied_card(card_id: int, handler: Annotated[SetHandler, Depends(get_set_handler)]):
    next_card = handler.get_next_unstudied_card(card_id=card_id)
    if next_card is None:
        return RedirectResponse(url="/sets")
    return RedirectResponse(url=f"/study/{next_card.id}")

### Run the server ###
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")