from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db

from schemas import UserCreate
from teacher_schemas import TeacherCreate
from course_schemas import CourseCreate
from student_schemas import StudentCreate
from enrollment_schemas import EnrollmentCreate

from models import User, Student, Teacher, Course, Enrollment

from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


app = FastAPI(
    title="Education Management Portal",
    description="AI-powered Education Management Portal",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Education Management Portal API is running"
    }


# ============================================================
# DATABASE TEST
# ============================================================

@app.get("/test-db")
def test_database():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "Database connection successful"
        }

    except Exception as e:
        return {
            "message": "Database connection failed",
            "error": str(e)
        }


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "user_id": existing_user.id,
        "role": existing_user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "message": "You are authenticated",
        "user_id": current_user.get("user_id"),
        "role": current_user.get("role")
    }


# ============================================================
# CREATE TEACHER PROFILE
# ============================================================

@app.post("/teachers")
def create_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Only teachers can create teacher profiles"
        )

    user_id = current_user.get("user_id")

    existing_teacher = db.query(Teacher).filter(
        Teacher.user_id == user_id
    ).first()

    if existing_teacher:
        raise HTTPException(
            status_code=400,
            detail="Teacher profile already exists"
        )

    existing_employee = db.query(Teacher).filter(
        Teacher.employee_id == teacher.employee_id
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )

    new_teacher = Teacher(
        user_id=user_id,
        employee_id=teacher.employee_id,
        department=teacher.department,
        designation=teacher.designation
    )

    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    return {
        "message": "Teacher profile created successfully",
        "teacher_id": new_teacher.id
    }


# ============================================================
# GET TEACHER PROFILE
# ============================================================

@app.get("/teachers/me")
def get_teacher_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Only teachers can access this endpoint"
        )

    user_id = current_user.get("user_id")

    teacher = db.query(Teacher).filter(
        Teacher.user_id == user_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    return teacher


# ============================================================
# CREATE STUDENT PROFILE
# ============================================================

@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can create student profiles"
        )

    user_id = current_user.get("user_id")

    existing_student = db.query(Student).filter(
        Student.user_id == user_id
    ).first()

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    existing_roll_number = db.query(Student).filter(
        Student.roll_number == student.roll_number
    ).first()

    if existing_roll_number:
        raise HTTPException(
            status_code=400,
            detail="Roll number already exists"
        )

    new_student = Student(
        user_id=user_id,
        roll_number=student.roll_number,
        department=student.department,
        year=student.year,
        section=student.section
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student profile created successfully",
        "student_id": new_student.id
    }


# ============================================================
# GET STUDENT PROFILE
# ============================================================

@app.get("/students/me")
def get_student_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can access student profile"
        )

    user_id = current_user.get("user_id")

    student = db.query(Student).filter(
        Student.user_id == user_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return student


# ============================================================
# CREATE COURSE
# ============================================================

@app.post("/courses")
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only teachers and admins can create courses"
        )

    teacher = db.query(Teacher).filter(
        Teacher.id == course.teacher_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    existing_course = db.query(Course).filter(
        Course.code == course.code
    ).first()

    if existing_course:
        raise HTTPException(
            status_code=400,
            detail="Course code already exists"
        )

    new_course = Course(
        name=course.name,
        code=course.code,
        description=course.description,
        teacher_id=course.teacher_id,
        credits=course.credits,
        semester=course.semester
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return {
        "message": "Course created successfully",
        "course_id": new_course.id
    }


# ============================================================
# GET ALL COURSES
# ============================================================

@app.get("/courses")
def get_courses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    courses = db.query(Course).all()

    return courses


# ============================================================
# ENROLL STUDENT IN COURSE
# ============================================================

@app.post("/enrollments")
def enroll_student(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Only students can enroll
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can enroll in courses"
        )

    user_id = current_user.get("user_id")

    # Find student profile
    student = db.query(Student).filter(
        Student.user_id == user_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # Check course exists
    course = db.query(Course).filter(
        Course.id == enrollment.course_id
    ).first()

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.course_id == enrollment.course_id
    ).first()

    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Student is already enrolled in this course"
        )

    # Create enrollment
    new_enrollment = Enrollment(
        student_id=student.id,
        course_id=enrollment.course_id
    )

    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return {
        "message": "Student enrolled successfully",
        "enrollment_id": new_enrollment.id
    }


# ============================================================
# GET MY ENROLLMENTS
# ============================================================

@app.get("/enrollments/me")
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=403,
            detail="Only students can access enrollments"
        )

    user_id = current_user.get("user_id")

    student = db.query(Student).filter(
        Student.user_id == user_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    return enrollments