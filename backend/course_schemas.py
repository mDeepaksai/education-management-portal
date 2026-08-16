from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    code: str
    description: str | None = None
    teacher_id: int
    credits: int
    semester: int