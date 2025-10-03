from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, HttpUrl
from database import create_tables, save_user, drop_tables, Base, engine



app = FastAPI()
templates = Jinja2Templates(directory="templates")


#remove before the final deployment 

# Create tables at startup
@app.on_event("startup")
def on_startup():
    create_tables()

@app.on_event("shutdown")
def on_shutdown():
    drop_tables()


class User(BaseModel):
    username: str
    password: str
    confirm_password: str
    email: EmailStr
    phonenumber: str
    website: HttpUrl
    adharid: int




@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/register")
def login(user: User):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    # Save user to database
    db_user = save_user(
        user.username,
        user.password,
        user.email,
        user.phonenumber,
        str(user.website),
        str(user.adharid)
    )
    if db_user == "username":
        raise HTTPException(status_code=400, detail="Username already exists.")
    if db_user == "email":
        raise HTTPException(status_code=400, detail="Email already exists.")
    if db_user is None:
        raise HTTPException(status_code=500, detail="Failed to save user.")
    return {"message": f"User {db_user.username} logged in successfully."}


# Remove before the final deployment
"""
Why is it needed?

It is useful during development to reset the database schema, especially if you change your models and want to start fresh.
In your code, it is called on application shutdown to automatically remove all tables when the FastAPI app stops.
Note:
This is not recommended for production, as it will erase all your data and tables. It is mainly for development and testing purposes.
"""
def drop_tables():
    Base.metadata.drop_all(bind=engine)
