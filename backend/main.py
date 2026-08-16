from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, Base, get_db

from models import (
    User,
    Student,
    Teacher,
    Course,
    Enrollment,
    Attendance,
    Assignment,
    AssignmentSubmission,
    Exam,
    ExamMarks
)

from schemas import UserCreate
from teacher_schemas import TeacherCreate
from student_schemas import StudentCreate
from course_schemas import CourseCreate
from enrollment_schemas import EnrollmentCreate
from attendance_schemas import AttendanceCreate

from assignment_schemas import (
    AssignmentCreate,
    AssignmentSubmissionCreate
)

from assignment_marks_schemas import AssignmentMarksUpdate

from exam_schemas import (
    ExamCreate,
    ExamMarksCreate
)

from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

from analytics import calculate_risk


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Education Management Portal",
    description="AI Powered Education Management Portal",
    version="1.0.0"
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

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
            "status": "success",
            "message": "Database connected successfully"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# REGISTER
# ============================================================

@app.post("/register")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(
        user_data.password
    )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
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
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):

    return current_user


# ============================================================
# CREATE TEACHER PROFILE
# ============================================================

@app.post("/teachers")
def create_teacher(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can create teacher profile"
        )

    existing_teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.get("user_id")
    ).first()

    if existing_teacher:

        raise HTTPException(
            status_code=400,
            detail="Teacher profile already exists"
        )

    teacher = Teacher(
        user_id=current_user.get("user_id"),
        employee_id=teacher_data.employee_id,
        department=teacher_data.department,
        designation=teacher_data.designation
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return {
        "message": "Teacher profile created successfully",
        "teacher_id": teacher.id
    }


# ============================================================
# CREATE STUDENT PROFILE
# ============================================================

@app.post("/students")
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can create student profile"
        )

    existing_student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if existing_student:

        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    student = Student(
        user_id=current_user.get("user_id"),
        roll_number=student_data.roll_number,
        department=student_data.department,
        year=student_data.year,
        section=student_data.section
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return {
        "message": "Student profile created successfully",
        "student_id": student.id
    }


# ============================================================
# CREATE COURSE
# ============================================================

@app.post("/courses")
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can create courses"
        )

    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.get("user_id")
    ).first()

    if not teacher:

        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    course = Course(
        name=course_data.name,
        code=course_data.code,
        description=course_data.description,
        teacher_id=teacher.id,
        credits=course_data.credits,
        semester=course_data.semester
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return {
        "message": "Course created successfully",
        "course_id": course.id
    }


# ============================================================
# GET COURSES
# ============================================================

@app.get("/courses")
def get_courses(
    db: Session = Depends(get_db)
):

    courses = db.query(Course).all()

    return courses


# ============================================================
# ENROLL STUDENT
# ============================================================

@app.post("/enrollments")
def enroll_student(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can enroll"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    course = db.query(Course).filter(
        Course.id == enrollment_data.course_id
    ).first()

    if not course:

        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.course_id == enrollment_data.course_id
    ).first()

    if existing_enrollment:

        raise HTTPException(
            status_code=400,
            detail="Student already enrolled"
        )

    enrollment = Enrollment(
        student_id=student.id,
        course_id=enrollment_data.course_id
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {
        "message": "Student enrolled successfully",
        "enrollment_id": enrollment.id
    }


# ============================================================
# MARK ATTENDANCE
# ============================================================

@app.post("/attendance")
def mark_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can mark attendance"
        )

    student = db.query(Student).filter(
        Student.id == attendance_data.student_id
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    course = db.query(Course).filter(
        Course.id == attendance_data.course_id
    ).first()

    if not course:

        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    attendance = Attendance(
        student_id=attendance_data.student_id,
        course_id=attendance_data.course_id,
        date=attendance_data.date,
        status=attendance_data.status
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {
        "message": "Attendance recorded successfully",
        "attendance_id": attendance.id
    }


# ============================================================
# CREATE ASSIGNMENT
# ============================================================

@app.post("/assignments")
def create_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can create assignments"
        )

    course = db.query(Course).filter(
        Course.id == assignment_data.course_id
    ).first()

    if not course:

        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    assignment = Assignment(
        course_id=assignment_data.course_id,
        title=assignment_data.title,
        description=assignment_data.description,
        due_date=assignment_data.due_date,
        max_marks=assignment_data.max_marks
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Assignment created successfully",
        "assignment_id": assignment.id
    }


# ============================================================
# SUBMIT ASSIGNMENT
# ============================================================

@app.post("/assignments/submit")
def submit_assignment(
    submission_data: AssignmentSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can submit assignments"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    assignment = db.query(Assignment).filter(
        Assignment.id == submission_data.assignment_id
    ).first()

    if not assignment:

        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    existing_submission = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.assignment_id ==
        submission_data.assignment_id,
        AssignmentSubmission.student_id ==
        student.id
    ).first()

    if existing_submission:

        raise HTTPException(
            status_code=400,
            detail="Assignment already submitted"
        )

    submission = AssignmentSubmission(
        assignment_id=submission_data.assignment_id,
        student_id=student.id,
        submission_date=submission_data.submission_date
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {
        "message": "Assignment submitted successfully",
        "submission_id": submission.id
    }


# ============================================================
# GIVE ASSIGNMENT MARKS
# ============================================================

@app.put("/assignments/submission/{submission_id}/marks")
def give_assignment_marks(
    submission_id: int,
    marks_data: AssignmentMarksUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can give marks"
        )

    submission = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.id == submission_id
    ).first()

    if not submission:

        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    assignment = db.query(Assignment).filter(
        Assignment.id == submission.assignment_id
    ).first()

    if not assignment:

        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    if marks_data.marks < 0 or marks_data.marks > assignment.max_marks:

        raise HTTPException(
            status_code=400,
            detail="Invalid marks"
        )

    submission.marks = marks_data.marks

    db.commit()
    db.refresh(submission)

    return {
        "message": "Assignment marks updated successfully",
        "submission_id": submission.id,
        "marks": submission.marks
    }


# ============================================================
# CREATE EXAM
# ============================================================

@app.post("/exams")
def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can create exams"
        )

    course = db.query(Course).filter(
        Course.id == exam_data.course_id
    ).first()

    if not course:

        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    exam = Exam(
        course_id=exam_data.course_id,
        name=exam_data.name,
        exam_type=exam_data.exam_type,
        date=exam_data.date,
        max_marks=exam_data.max_marks
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    return {
        "message": "Exam created successfully",
        "exam_id": exam.id
    }


# ============================================================
# GET EXAMS FOR COURSE
# ============================================================

@app.get("/exams/course/{course_id}")
def get_course_exams(
    course_id: int,
    db: Session = Depends(get_db)
):

    exams = db.query(Exam).filter(
        Exam.course_id == course_id
    ).all()

    return exams


# ============================================================
# ADD EXAM MARKS
# ============================================================

@app.post("/exam-marks")
def add_exam_marks(
    marks_data: ExamMarksCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "teacher":

        raise HTTPException(
            status_code=403,
            detail="Only teachers can enter exam marks"
        )

    exam = db.query(Exam).filter(
        Exam.id == marks_data.exam_id
    ).first()

    if not exam:

        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )

    student = db.query(Student).filter(
        Student.id == marks_data.student_id
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if marks_data.marks < 0 or marks_data.marks > exam.max_marks:

        raise HTTPException(
            status_code=400,
            detail="Invalid marks"
        )

    existing_marks = db.query(ExamMarks).filter(
        ExamMarks.exam_id == marks_data.exam_id,
        ExamMarks.student_id == marks_data.student_id
    ).first()

    if existing_marks:

        existing_marks.marks = marks_data.marks

        db.commit()
        db.refresh(existing_marks)

        return {
            "message": "Exam marks updated successfully",
            "exam_marks_id": existing_marks.id,
            "marks": existing_marks.marks
        }

    exam_marks = ExamMarks(
        exam_id=marks_data.exam_id,
        student_id=marks_data.student_id,
        marks=marks_data.marks
    )

    db.add(exam_marks)
    db.commit()
    db.refresh(exam_marks)

    return {
        "message": "Exam marks added successfully",
        "exam_marks_id": exam_marks.id,
        "marks": exam_marks.marks
    }


# ============================================================
# GET MY EXAM MARKS
# ============================================================

@app.get("/exam-marks/me")
def get_my_exam_marks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access their marks"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    marks = db.query(ExamMarks).filter(
        ExamMarks.student_id == student.id
    ).all()

    result = []

    for mark in marks:

        exam = db.query(Exam).filter(
            Exam.id == mark.exam_id
        ).first()

        result.append({
            "exam_id": mark.exam_id,
            "exam_name": exam.name if exam else None,
            "exam_type": exam.exam_type if exam else None,
            "marks": mark.marks,
            "max_marks": exam.max_marks if exam else None
        })

    return result


# ============================================================
# STUDENT ANALYTICS
# ============================================================

@app.get("/analytics/student/me")
def student_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # --------------------------------------------------------
    # CHECK ROLE
    # --------------------------------------------------------

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access analytics"
        )


    # --------------------------------------------------------
    # FIND STUDENT
    # --------------------------------------------------------

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )


    # ========================================================
    # ATTENDANCE
    # ========================================================

    attendance_records = db.query(Attendance).filter(
        Attendance.student_id == student.id
    ).all()

    if attendance_records:

        present = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        attendance_percentage = (
            present / len(attendance_records)
        ) * 100

    else:

        attendance_percentage = 0


    # ========================================================
    # ASSIGNMENT PERFORMANCE
    # ========================================================

    submissions = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student.id,
        AssignmentSubmission.marks.isnot(None)
    ).all()

    assignment_percentage = 0

    if submissions:

        percentages = []

        for submission in submissions:

            assignment = db.query(
                Assignment
            ).filter(
                Assignment.id == submission.assignment_id
            ).first()

            if assignment and assignment.max_marks > 0:

                percentage = (
                    submission.marks /
                    assignment.max_marks
                ) * 100

                percentages.append(percentage)

        if percentages:

            assignment_percentage = (
                sum(percentages) /
                len(percentages)
            )


    # ========================================================
    # EXAM PERFORMANCE
    # ========================================================

    exam_marks = db.query(
        ExamMarks
    ).filter(
        ExamMarks.student_id == student.id
    ).all()

    exam_percentage = 0

    if exam_marks:

        percentages = []

        for mark in exam_marks:

            exam = db.query(Exam).filter(
                Exam.id == mark.exam_id
            ).first()

            if exam and exam.max_marks > 0:

                percentage = (
                    mark.marks /
                    exam.max_marks
                ) * 100

                percentages.append(percentage)

        if percentages:

            exam_percentage = (
                sum(percentages) /
                len(percentages)
            )


    # ========================================================
    # RISK CALCULATION
    # ========================================================

    risk = calculate_risk(
        attendance_percentage,
        assignment_percentage,
        exam_percentage
    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {

        "student_id": student.id,

        "attendance": round(
            attendance_percentage,
            2
        ),

        "assignment_performance": round(
            assignment_percentage,
            2
        ),

        "exam_performance": round(
            exam_percentage,
            2
        ),

        "risk_score": risk["risk_score"],

        "risk_level": risk["risk_level"],

        "reasons": risk["reasons"]

    }