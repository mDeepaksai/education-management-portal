from fastapi import FastAPI
from sqlalchemy import text

from database import engine

app = FastAPI()


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
        return {"message": "Database connection failed", "error": str(e)}