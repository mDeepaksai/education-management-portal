from pydantic import BaseModel


class AssignmentMarksUpdate(BaseModel):
    marks: int