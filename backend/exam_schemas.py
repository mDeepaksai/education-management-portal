from pydantic import BaseModel


class ExamCreate(BaseModel):
    course_id: int
    name: str
    exam_type: str
    date: str
    max_marks: int


class ExamMarksCreate(BaseModel):
    exam_id: int
    student_id: int
    marks: int