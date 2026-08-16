from pydantic import BaseModel


class StudentCreate(BaseModel):
    roll_number: str
    department: str
    year: int
    section: str