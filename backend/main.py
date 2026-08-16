from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db
from schemas import UserCreate
from models import User

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Education Management Portal API is running"}


@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"message": "Database connection successful"}

    except Exception as e:
        return {
            "message": "Database connection failed",
            "error": str(e)
        }


@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }