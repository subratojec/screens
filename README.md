# 📧 Email Verification API

## 🚀 Quick Setup Guide

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start PostgreSQL Database

**Option A: Using Docker**
```bash
docker run --name mypostgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```

**Option B: Without Docker**
- Download and install PostgreSQL
- Use the same naming convention and password as above

### 4. Run FastAPI Server
```bash
uvicorn main:app --reload
```

## 🌐 Access Your API
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **API Documentation**: http://127.0.0.1:8000/api-docs

## 📋 API Endpoints
- `POST /verify-email` - Send OTP to email
- `POST /verify-email-otp` - Verify OTP code
- `POST /register` - Complete user registration

---
**Ready to use! 🎉**