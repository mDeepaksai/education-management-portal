from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    course_id: int