
from typing import Set
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
import random

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME="nu3vojdzfrjs2bcy",
    MAIL_PASSWORD="xxd53mtntepjrr1q",
    MAIL_FROM="nu3vojdzfrjs2bcy@mailmug.net",
    MAIL_PORT=2525,
    MAIL_SERVER="smtp.mailmug.net",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# In-memory stores for OTPs and verified emails (for demo; use Redis or DB in production)
otp_store = {}
verified_emails: Set[str] = set()


def generate_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


async def send_otp_email(email: str, otp: str):
    """Send OTP email to the specified email address."""
    html = f"""<html><body>
        <p>Your OTP for email verification is: <b>{otp}</b></p>
        <p>This OTP is valid for a short time. Please enter it to complete your registration.</p>
    </body></html>"""
    
    message = MessageSchema(
        subject="Your OTP for Email Verification",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)


def store_otp(email: str, otp: str):
    """Store OTP for the given email."""
    otp_store[email] = otp


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP for the given email. Returns True if valid, False otherwise."""
    stored_otp = otp_store.get(email)
    if not stored_otp:
        return False
    if otp != stored_otp:
        return False
    
    # OTP is correct, mark email as verified and clean up
    verified_emails.add(email)
    del otp_store[email]
    return True


def is_email_verified(email: str) -> bool:
    """Check if email has been verified."""
    return email in verified_emails


def remove_verified_email(email: str):
    """Remove email from verified list (after successful registration)."""
    verified_emails.discard(email)


def get_stored_otp(email: str) -> str:
    """Get stored OTP for email (for debugging purposes)."""
    return otp_store.get(email)


def clear_otp(email: str):
    """Clear OTP for email."""
    if email in otp_store:
        del otp_store[email]


# Pydantic models
class EmailSchema(BaseModel):
    email: EmailStr


class OTPVerifySchema(BaseModel):
    email: EmailStr
    otp: str