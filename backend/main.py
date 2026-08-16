from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db
from schemas import UserCreate
from models import User
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


app = FastAPI(
    title="Education Management Portal",
    description="AI-powered Education Management Portal",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


# ---------------- HOME ----------------

@app.get("/")
def home():
    return {
        "message": "Education Management Portal API is running"
    }


# ---------------- DATABASE TEST ----------------

@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "Database connection successful"
        }

    except Exception as e:
        return {
            "message": "Database connection failed",
            "error": str(e)
        }


# ---------------- REGISTER ----------------

@app.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# ---------------- LOGIN ----------------

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Swagger sends the email in the username field
    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "user_id": existing_user.id,
        "role": existing_user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------- PROTECTED USER ----------------

@app.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "user_id": current_user.get("user_id"),
        "role": current_user.get("role")
    }