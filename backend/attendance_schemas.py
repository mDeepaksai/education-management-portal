from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    student_id: int
    course_id: int
    date: str
    status: str