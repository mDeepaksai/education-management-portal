from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    student = relationship(
        "Student",
        back_populates="user",
        uselist=False
    )

    teacher = relationship(
        "Teacher",
        back_populates="user",
        uselist=False
    )


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
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

    user = relationship(
        "User",
        back_populates="student"
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
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

    user = relationship(
        "User",
        back_populates="teacher"
    )
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
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
class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)

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