from typing import Annotated
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, HttpUrl, Field 
from starlette.responses import JSONResponse

from database import create_tables, save_user, drop_tables, Base, engine
from mail_verify import (
    EmailSchema, OTPVerifySchema, generate_otp, send_otp_email, 
    store_otp, verify_otp, is_email_verified, remove_verified_email
)


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


# Pydantic models
class User(BaseModel):
    username: Annotated[str,Field(...,min_length=3,max_length=50)]
    password: Annotated[str,Field(...,min_length=8,max_length=50)]
    confirm_password: Annotated[str,Field(...,min_length=8,max_length=50)]
    email: Annotated[EmailStr,Field(...,min_length=3,max_length=50)]
    phonenumber: Annotated[str,Field(...,min_length=10,max_length=10)]
    website: Annotated[HttpUrl,Field(min_length=3,max_length=50)]
    adharid: Annotated[int,Field(...,min_length=12,max_length=12)]




@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api-docs")
async def api_docs():
    """API Documentation endpoint."""
    return {
        "title": "Email Verification & Registration API",
        "description": "API for email verification and user registration",
        "endpoints": {
            "POST /verify-email": {
                "description": "Send OTP to email address for verification",
                "request_body": {"email": "string (valid email address)"},
                "response": {"message": "OTP sent to email"}
            },
            "POST /verify-email-otp": {
                "description": "Verify OTP code for email verification",
                "request_body": {"email": "string", "otp": "string (6-digit code)"},
                "response": {"message": "Email verified successfully"}
            },
            "POST /register": {
                "description": "Complete user registration (requires verified email)",
                "request_body": {
                    "username": "string",
                    "password": "string",
                    "confirm_password": "string",
                    "email": "string (must be verified)",
                    "phonenumber": "string",
                    "website": "string (valid URL)",
                    "adharid": "integer"
                },
                "response": {"message": "User registered successfully"}
            }
        },
        "interactive_docs": "/docs"
    }


# Step 1: Send OTP for email verification
@app.post("/verify-email")
async def verify_email(email_data: EmailSchema):
    email = email_data.email
    
    # Check if email is already registered
    from database import SessionLocal, User as DBUser
    db = SessionLocal()
    existing_user = db.query(DBUser).filter(DBUser.email == email).first()
    db.close()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    # Generate OTP and send email
    otp = generate_otp()
    try:
        await send_otp_email(email, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {e}")
    
    # Store OTP for this email
    store_otp(email, otp)
    
    return JSONResponse(
        status_code=200, 
        content={"message": f"OTP sent to {email}. Please verify your email to continue with registration."}
    )


# Step 2: Verify OTP for email verification
@app.post("/verify-email-otp")
async def verify_email_otp(data: OTPVerifySchema):
    if not verify_otp(data.email, data.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired.")
    
    return JSONResponse(
        status_code=200, 
        content={"message": "Email verified successfully. You can now complete your registration."}
    )


# Step 3: Complete registration (only after email verification)
@app.post("/register")
async def register(user: User):
    # Check if email is verified
    if not is_email_verified(user.email):
        raise HTTPException(status_code=400, detail="Please verify your email first before registering.")
    
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
    
    # Handle database response
    if db_user == "username":
        raise HTTPException(status_code=400, detail="Username already exists.")
    if db_user == "email":
        raise HTTPException(status_code=400, detail="Email already exists.")
    if db_user is None:
        raise HTTPException(status_code=500, detail="Failed to save user.")
    
    # Remove from verified emails after successful registration
    remove_verified_email(user.email)
    
    return {"message": f"User {db_user.username} registered successfully."}





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
