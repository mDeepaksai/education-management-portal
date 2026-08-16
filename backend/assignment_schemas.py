from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    description: str | None = None
    due_date: str
    max_marks: int


class AssignmentSubmissionCreate(BaseModel):
    assignment_id: int
    submission_date: str