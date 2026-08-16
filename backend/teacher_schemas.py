from pydantic import BaseModel


class TeacherCreate(BaseModel):
    employee_id: str
    department: str
    designation: str