from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import (
    User,
    Student,
    Teacher,
    Course,
    Enrollment
)
from security import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# ADMIN AUTHORIZATION
# ============================================================

def verify_admin(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can access this endpoint"
        )

    return current_user


# ============================================================
# GET ALL USERS
# ============================================================

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):

    users = db.query(User).all()

    result = []

    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        })

    return {
        "total_users": len(result),
        "users": result
    }


# ============================================================
# GET ALL STUDENTS
# ============================================================

@router.get("/students")
def get_all_students(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):

    students = db.query(Student).all()

    result = []

    for student in students:

        user = db.query(User).filter(
            User.id == student.user_id
        ).first()

        result.append({
            "student_id": student.id,
            "user_id": student.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "roll_number": student.roll_number,
            "department": student.department,
            "year": student.year,
            "section": student.section
        })

    return {
        "total_students": len(result),
        "students": result
    }


# ============================================================
# GET ALL TEACHERS
# ============================================================

@router.get("/teachers")
def get_all_teachers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):

    teachers = db.query(Teacher).all()

    result = []

    for teacher in teachers:

        user = db.query(User).filter(
            User.id == teacher.user_id
        ).first()

        result.append({
            "teacher_id": teacher.id,
            "user_id": teacher.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "employee_id": teacher.employee_id,
            "department": teacher.department,
            "designation": teacher.designation
        })

    return {
        "total_teachers": len(result),
        "teachers": result
    }


# ============================================================
# GET ALL COURSES
# ============================================================

@router.get("/courses")
def get_all_courses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):

    courses = db.query(Course).all()

    result = []

    for course in courses:

        teacher = db.query(Teacher).filter(
            Teacher.id == course.teacher_id
        ).first()

        teacher_user = None

        if teacher:
            teacher_user = db.query(User).filter(
                User.id == teacher.user_id
            ).first()

        enrollment_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id
        ).count()

        result.append({
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            "description": course.description,
            "credits": course.credits,
            "semester": course.semester,
            "teacher_id": course.teacher_id,
            "teacher_name": (
                teacher_user.name
                if teacher_user
                else None
            ),
            "enrolled_students": enrollment_count
        })

    return {
        "total_courses": len(result),
        "courses": result
    }


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):

    total_users = db.query(User).count()

    total_students = db.query(Student).count()

    total_teachers = db.query(Teacher).count()

    total_courses = db.query(Course).count()

    total_enrollments = db.query(Enrollment).count()

    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments
    }