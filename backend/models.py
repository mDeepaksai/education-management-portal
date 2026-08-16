from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False
    )


# ============================================================
# STUDENT
# ============================================================

class Student(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    roll_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    department = Column(
        String(100),
        nullable=False
    )

    year = Column(
        Integer,
        nullable=False
    )

    section = Column(
        String(20),
        nullable=False
    )


# ============================================================
# TEACHER
# ============================================================

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    employee_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    department = Column(
        String(100),
        nullable=False
    )

    designation = Column(
        String(100),
        nullable=False
    )


# ============================================================
# COURSE
# ============================================================

class Course(Base):
    __tablename__ = "courses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    code = Column(
        String(50),
        unique=True,
        nullable=False
    )

    description = Column(
        String(500),
        nullable=True
    )

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    credits = Column(
        Integer,
        nullable=False
    )

    semester = Column(
        Integer,
        nullable=False
    )


# ============================================================
# ENROLLMENT
# ============================================================

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )


# ============================================================
# ATTENDANCE
# ============================================================

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    date = Column(
        String(20),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )
# ============================================================
# ASSIGNMENT
# ============================================================

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=True
    )

    due_date = Column(
        String(30),
        nullable=False
    )

    max_marks = Column(
        Integer,
        nullable=False
    )


# ============================================================
# ASSIGNMENT SUBMISSION
# ============================================================

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    assignment_id = Column(
        Integer,
        ForeignKey("assignments.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    submission_date = Column(
        String(30),
        nullable=False
    )

    marks = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="submitted"
    )
# ============================================================
# EXAM
# ============================================================

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    name = Column(
        String(200),
        nullable=False
    )

    exam_type = Column(
        String(50),
        nullable=False
    )

    date = Column(
        String(30),
        nullable=False
    )

    max_marks = Column(
        Integer,
        nullable=False
    )


# ============================================================
# EXAM MARKS
# ============================================================

class ExamMarks(Base):
    __tablename__ = "exam_marks"

    id = Column(Integer, primary_key=True, index=True)

    exam_id = Column(
        Integer,
        ForeignKey("exams.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    marks = Column(
        Integer,
        nullable=False
    )