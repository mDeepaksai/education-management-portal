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
from trend import calculate_trend
from course_analytics import calculate_course_performance

from recommendations import generate_recommendations
from ai_service import generate_ai_recommendation


# ============================================================
# FASTAPI APPLICATION
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

    if (
        marks_data.marks < 0
        or marks_data.marks > assignment.max_marks
    ):

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

    if (
        marks_data.marks < 0
        or marks_data.marks > exam.max_marks
    ):

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
# STUDENT OVERALL PERFORMANCE ANALYTICS
# ============================================================

@app.get("/analytics/student/me")
def student_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access analytics"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

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

    risk = calculate_risk(
        attendance_percentage,
        assignment_percentage,
        exam_percentage
    )

    return {
        "student_id": student.id,
        "attendance": round(attendance_percentage, 2),
        "assignment_performance": round(
            assignment_percentage, 2
        ),
        "exam_performance": round(
            exam_percentage, 2
        ),
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "reasons": risk["reasons"]
    }


# ============================================================
# STUDENT TREND
# ============================================================

@app.get("/analytics/student/trend")
def student_trend(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access trend analysis"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    exam_marks = db.query(
        ExamMarks
    ).filter(
        ExamMarks.student_id == student.id
    ).all()

    scores = []

    for mark in exam_marks:

        exam = db.query(Exam).filter(
            Exam.id == mark.exam_id
        ).first()

        if exam and exam.max_marks > 0:

            percentage = (
                mark.marks /
                exam.max_marks
            ) * 100

            scores.append({
                "date": exam.date,
                "score": percentage
            })

    scores.sort(
        key=lambda x: x["date"]
    )

    score_values = [
        item["score"]
        for item in scores
    ]

    trend_result = calculate_trend(
        score_values
    )

    return {
        "student_id": student.id,
        "trend": trend_result["trend"],
        "recent_average": trend_result["recent_average"],
        "previous_average": trend_result["previous_average"],
        "difference": trend_result["difference"],
        "number_of_exams": len(score_values)
    }


# ============================================================
# COURSE-WISE STUDENT ANALYTICS
# ============================================================

@app.get("/analytics/student/courses")
def student_course_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access course analytics"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id
    ).all()

    course_results = []

    for enrollment in enrollments:

        course = db.query(Course).filter(
            Course.id == enrollment.course_id
        ).first()

        if not course:
            continue

        course_id = course.id

        attendance_records = db.query(
            Attendance
        ).filter(
            Attendance.student_id == student.id,
            Attendance.course_id == course_id
        ).all()

        if attendance_records:

            present = sum(
                1
                for record in attendance_records
                if record.status.lower() == "present"
            )

            attendance_percentage = (
                present /
                len(attendance_records)
            ) * 100

        else:

            attendance_percentage = 0

        assignments = db.query(
            Assignment
        ).filter(
            Assignment.course_id == course_id
        ).all()

        assignment_percentages = []

        for assignment in assignments:

            submission = db.query(
                AssignmentSubmission
            ).filter(
                AssignmentSubmission.assignment_id ==
                assignment.id,
                AssignmentSubmission.student_id ==
                student.id
            ).first()

            if (
                submission
                and submission.marks is not None
                and assignment.max_marks > 0
            ):

                assignment_percentages.append(
                    (
                        submission.marks /
                        assignment.max_marks
                    ) * 100
                )

        assignment_percentage = (
            sum(assignment_percentages) /
            len(assignment_percentages)
            if assignment_percentages
            else 0
        )

        exams = db.query(Exam).filter(
            Exam.course_id == course_id
        ).all()

        exam_percentages = []

        for exam in exams:

            marks = db.query(
                ExamMarks
            ).filter(
                ExamMarks.exam_id == exam.id,
                ExamMarks.student_id == student.id
            ).first()

            if (
                marks
                and exam.max_marks > 0
            ):

                exam_percentages.append(
                    (
                        marks.marks /
                        exam.max_marks
                    ) * 100
                )

        exam_percentage = (
            sum(exam_percentages) /
            len(exam_percentages)
            if exam_percentages
            else 0
        )

        performance = calculate_course_performance(
            attendance_percentage,
            assignment_percentage,
            exam_percentage
        )

        course_results.append({
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            **performance
        })

    if course_results:

        strongest_course = max(
            course_results,
            key=lambda x: x["overall_score"]
        )

        weakest_course = min(
            course_results,
            key=lambda x: x["overall_score"]
        )

        strongest_course_name = (
            strongest_course["course_name"]
        )

        weakest_course_name = (
            weakest_course["course_name"]
        )

    else:

        strongest_course_name = None
        weakest_course_name = None

    return {
        "student_id": student.id,
        "courses": course_results,
        "strongest_course": strongest_course_name,
        "weakest_course": weakest_course_name
    }


# ============================================================
# STUDENT RECOMMENDATIONS
# ============================================================

@app.get("/analytics/student/recommendations")
def student_recommendations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access recommendations"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    attendance_records = db.query(
        Attendance
    ).filter(
        Attendance.student_id == student.id
    ).all()

    if attendance_records:

        present = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        attendance_percentage = (
            present /
            len(attendance_records)
        ) * 100

    else:

        attendance_percentage = 0

    submissions = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student.id,
        AssignmentSubmission.marks.isnot(None)
    ).all()

    assignment_percentages = []

    for submission in submissions:

        assignment = db.query(
            Assignment
        ).filter(
            Assignment.id == submission.assignment_id
        ).first()

        if assignment and assignment.max_marks > 0:

            assignment_percentages.append(
                (
                    submission.marks /
                    assignment.max_marks
                ) * 100
            )

    assignment_percentage = (
        sum(assignment_percentages) /
        len(assignment_percentages)
        if assignment_percentages
        else 0
    )

    exam_marks = db.query(
        ExamMarks
    ).filter(
        ExamMarks.student_id == student.id
    ).all()

    exam_percentages = []

    for mark in exam_marks:

        exam = db.query(
            Exam
        ).filter(
            Exam.id == mark.exam_id
        ).first()

        if exam and exam.max_marks > 0:

            exam_percentages.append(
                (
                    mark.marks /
                    exam.max_marks
                ) * 100
            )

    exam_percentage = (
        sum(exam_percentages) /
        len(exam_percentages)
        if exam_percentages
        else 0
    )

    risk = calculate_risk(
        attendance_percentage,
        assignment_percentage,
        exam_percentage
    )

    enrollments = db.query(
        Enrollment
    ).filter(
        Enrollment.student_id == student.id
    ).all()

    course_results = []

    for enrollment in enrollments:

        course = db.query(
            Course
        ).filter(
            Course.id == enrollment.course_id
        ).first()

        if not course:
            continue

        course_id = course.id

        course_attendance = db.query(
            Attendance
        ).filter(
            Attendance.student_id == student.id,
            Attendance.course_id == course_id
        ).all()

        if course_attendance:

            present = sum(
                1
                for record in course_attendance
                if record.status.lower() == "present"
            )

            course_attendance_percentage = (
                present /
                len(course_attendance)
            ) * 100

        else:

            course_attendance_percentage = 0

        assignments = db.query(
            Assignment
        ).filter(
            Assignment.course_id == course_id
        ).all()

        assignment_scores = []

        for assignment in assignments:

            submission = db.query(
                AssignmentSubmission
            ).filter(
                AssignmentSubmission.assignment_id ==
                assignment.id,
                AssignmentSubmission.student_id ==
                student.id
            ).first()

            if (
                submission
                and submission.marks is not None
                and assignment.max_marks > 0
            ):

                assignment_scores.append(
                    (
                        submission.marks /
                        assignment.max_marks
                    ) * 100
                )

        course_assignment_percentage = (
            sum(assignment_scores) /
            len(assignment_scores)
            if assignment_scores
            else 0
        )

        exams = db.query(Exam).filter(
            Exam.course_id == course_id
        ).all()

        exam_scores = []

        for exam in exams:

            marks = db.query(
                ExamMarks
            ).filter(
                ExamMarks.exam_id == exam.id,
                ExamMarks.student_id == student.id
            ).first()

            if marks and exam.max_marks > 0:

                exam_scores.append(
                    (
                        marks.marks /
                        exam.max_marks
                    ) * 100
                )

        course_exam_percentage = (
            sum(exam_scores) /
            len(exam_scores)
            if exam_scores
            else 0
        )

        performance = calculate_course_performance(
            course_attendance_percentage,
            course_assignment_percentage,
            course_exam_percentage
        )

        course_results.append({
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            **performance
        })

    if course_results:

        strongest_course = max(
            course_results,
            key=lambda x: x["overall_score"]
        )

        weakest_course = min(
            course_results,
            key=lambda x: x["overall_score"]
        )

        strongest_course_name = (
            strongest_course["course_name"]
        )

        weakest_course_name = (
            weakest_course["course_name"]
        )

    else:

        strongest_course_name = None
        weakest_course_name = None

    exam_scores_for_trend = []

    for mark in exam_marks:

        exam = db.query(
            Exam
        ).filter(
            Exam.id == mark.exam_id
        ).first()

        if exam and exam.max_marks > 0:

            percentage = (
                mark.marks /
                exam.max_marks
            ) * 100

            exam_scores_for_trend.append({
                "date": exam.date,
                "score": percentage
            })

    exam_scores_for_trend.sort(
        key=lambda x: x["date"]
    )

    score_values = [
        item["score"]
        for item in exam_scores_for_trend
    ]

    trend_result = calculate_trend(
        score_values
    )

    result = generate_recommendations(
        attendance=round(
            attendance_percentage,
            2
        ),
        assignment_performance=round(
            assignment_percentage,
            2
        ),
        exam_performance=round(
            exam_percentage,
            2
        ),
        risk_score=risk["risk_score"],
        risk_level=risk["risk_level"],
        reasons=risk["reasons"],
        strongest_course=strongest_course_name,
        weakest_course=weakest_course_name,
        trend=trend_result["trend"]
    )

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
        "reasons": risk["reasons"],
        "strongest_course": strongest_course_name,
        "weakest_course": weakest_course_name,
        "trend": trend_result["trend"],
        "recommendations": result
    }


# ============================================================
# AI STUDENT RECOMMENDATION
# ============================================================

@app.get("/ai/student/recommendation")
def ai_student_recommendation(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "student":

        raise HTTPException(
            status_code=403,
            detail="Only students can access AI recommendations"
        )

    student = db.query(Student).filter(
        Student.user_id == current_user.get("user_id")
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    attendance_records = db.query(
        Attendance
    ).filter(
        Attendance.student_id == student.id
    ).all()

    if attendance_records:

        present = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        attendance_percentage = (
            present /
            len(attendance_records)
        ) * 100

    else:

        attendance_percentage = 0

    # --------------------------------------------------------
    # ASSIGNMENTS
    # --------------------------------------------------------

    submissions = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student.id,
        AssignmentSubmission.marks.isnot(None)
    ).all()

    assignment_percentages = []

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

            assignment_percentages.append(
                percentage
            )

    if assignment_percentages:

        assignment_percentage = (
            sum(assignment_percentages) /
            len(assignment_percentages)
        )

    else:

        assignment_percentage = 0

    # --------------------------------------------------------
    # EXAMS
    # --------------------------------------------------------

    exam_marks = db.query(
        ExamMarks
    ).filter(
        ExamMarks.student_id == student.id
    ).all()

    exam_percentages = []

    for mark in exam_marks:

        exam = db.query(
            Exam
        ).filter(
            Exam.id == mark.exam_id
        ).first()

        if exam and exam.max_marks > 0:

            percentage = (
                mark.marks /
                exam.max_marks
            ) * 100

            exam_percentages.append(
                percentage
            )

    if exam_percentages:

        exam_percentage = (
            sum(exam_percentages) /
            len(exam_percentages)
        )

    else:

        exam_percentage = 0

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk = calculate_risk(
        attendance_percentage,
        assignment_percentage,
        exam_percentage
    )

    # --------------------------------------------------------
    # COURSE ANALYTICS
    # --------------------------------------------------------

    enrollments = db.query(
        Enrollment
    ).filter(
        Enrollment.student_id == student.id
    ).all()

    course_results = []

    for enrollment in enrollments:

        course = db.query(
            Course
        ).filter(
            Course.id == enrollment.course_id
        ).first()

        if not course:
            continue

        course_id = course.id

        course_attendance = db.query(
            Attendance
        ).filter(
            Attendance.student_id == student.id,
            Attendance.course_id == course_id
        ).all()

        if course_attendance:

            present = sum(
                1
                for record in course_attendance
                if record.status.lower() == "present"
            )

            course_attendance_percentage = (
                present /
                len(course_attendance)
            ) * 100

        else:

            course_attendance_percentage = 0

        assignments = db.query(
            Assignment
        ).filter(
            Assignment.course_id == course_id
        ).all()

        assignment_scores = []

        for assignment in assignments:

            submission = db.query(
                AssignmentSubmission
            ).filter(
                AssignmentSubmission.assignment_id ==
                assignment.id,
                AssignmentSubmission.student_id ==
                student.id
            ).first()

            if (
                submission
                and submission.marks is not None
                and assignment.max_marks > 0
            ):

                percentage = (
                    submission.marks /
                    assignment.max_marks
                ) * 100

                assignment_scores.append(
                    percentage
                )

        if assignment_scores:

            course_assignment_percentage = (
                sum(assignment_scores) /
                len(assignment_scores)
            )

        else:

            course_assignment_percentage = 0

        exams = db.query(Exam).filter(
            Exam.course_id == course_id
        ).all()

        exam_scores = []

        for exam in exams:

            marks = db.query(
                ExamMarks
            ).filter(
                ExamMarks.exam_id == exam.id,
                ExamMarks.student_id == student.id
            ).first()

            if (
                marks
                and exam.max_marks > 0
            ):

                percentage = (
                    marks.marks /
                    exam.max_marks
                ) * 100

                exam_scores.append(
                    percentage
                )

        if exam_scores:

            course_exam_percentage = (
                sum(exam_scores) /
                len(exam_scores)
            )

        else:

            course_exam_percentage = 0

        performance = calculate_course_performance(
            course_attendance_percentage,
            course_assignment_percentage,
            course_exam_percentage
        )

        course_results.append({
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            **performance
        })

    if course_results:

        strongest_course = max(
            course_results,
            key=lambda x: x["overall_score"]
        )

        weakest_course = min(
            course_results,
            key=lambda x: x["overall_score"]
        )

        strongest_course_name = (
            strongest_course["course_name"]
        )

        weakest_course_name = (
            weakest_course["course_name"]
        )

    else:

        strongest_course_name = None
        weakest_course_name = None

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    exam_scores_for_trend = []

    for mark in exam_marks:

        exam = db.query(
            Exam
        ).filter(
            Exam.id == mark.exam_id
        ).first()

        if exam and exam.max_marks > 0:

            percentage = (
                mark.marks /
                exam.max_marks
            ) * 100

            exam_scores_for_trend.append({
                "date": exam.date,
                "score": percentage
            })

    exam_scores_for_trend.sort(
        key=lambda x: x["date"]
    )

    score_values = [
        item["score"]
        for item in exam_scores_for_trend
    ]

    trend_result = calculate_trend(
        score_values
    )

    # --------------------------------------------------------
    # GEMINI AI
    # --------------------------------------------------------

    try:

        ai_result = generate_ai_recommendation(
            attendance=round(
                attendance_percentage,
                2
            ),
            assignment_performance=round(
                assignment_percentage,
                2
            ),
            exam_performance=round(
                exam_percentage,
                2
            ),
            risk_score=risk["risk_score"],
            risk_level=risk["risk_level"],
            reasons=risk["reasons"],
            strongest_course=strongest_course_name,
            weakest_course=weakest_course_name,
            trend=trend_result["trend"]
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI recommendation failed: {str(e)}"
        )

    return {

        "student_id": student.id,

        "performance": {

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
            )
        },

        "risk": {

            "risk_score":
                risk["risk_score"],

            "risk_level":
                risk["risk_level"],

            "reasons":
                risk["reasons"]
        },

        "course_analysis": {

            "strongest_course":
                strongest_course_name,

            "weakest_course":
                weakest_course_name
        },

        "trend":
            trend_result["trend"],

        "ai_recommendation":
            ai_result
    }


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.get("/admin/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access admin dashboard"
        )

    return {
        "total_users": db.query(User).count(),
        "total_students": db.query(Student).count(),
        "total_teachers": db.query(Teacher).count(),
        "total_courses": db.query(Course).count(),
        "total_enrollments": db.query(Enrollment).count(),
        "total_assignments": db.query(Assignment).count(),
        "total_submissions": db.query(
            AssignmentSubmission
        ).count(),
        "total_exams": db.query(Exam).count(),
        "total_exam_marks": db.query(
            ExamMarks
        ).count()
    }


# ============================================================
# ADMIN - ALL USERS
# ============================================================

@app.get("/admin/users")
def admin_get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access users"
        )

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]


# ============================================================
# ADMIN - ALL STUDENTS
# ============================================================

@app.get("/admin/students")
def admin_get_students(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access students"
        )

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

    return result


# ============================================================
# ADMIN - ALL TEACHERS
# ============================================================

@app.get("/admin/teachers")
def admin_get_teachers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access teachers"
        )

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

    return result


# ============================================================
# ADMIN - ALL COURSES
# ============================================================

@app.get("/admin/courses")
def admin_get_courses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access courses"
        )

    courses = db.query(Course).all()

    result = []

    for course in courses:

        teacher = db.query(Teacher).filter(
            Teacher.id == course.teacher_id
        ).first()

        teacher_name = None

        if teacher:

            user = db.query(User).filter(
                User.id == teacher.user_id
            ).first()

            if user:
                teacher_name = user.name

        enrollment_count = db.query(
            Enrollment
        ).filter(
            Enrollment.course_id == course.id
        ).count()

        result.append({
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            "description": course.description,
            "credits": course.credits,
            "semester": course.semester,
            "teacher": teacher_name,
            "enrolled_students": enrollment_count
        })

    return result


# ============================================================
# ADMIN - STUDENT RISK OVERVIEW
# ============================================================

@app.get("/admin/student-risk")
def admin_student_risk(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access student risk data"
        )

    students = db.query(Student).all()

    result = []

    for student in students:

        attendance_records = db.query(
            Attendance
        ).filter(
            Attendance.student_id == student.id
        ).all()

        if attendance_records:

            present = sum(
                1
                for record in attendance_records
                if record.status.lower() == "present"
            )

            attendance_percentage = (
                present /
                len(attendance_records)
            ) * 100

        else:

            attendance_percentage = 0

        submissions = db.query(
            AssignmentSubmission
        ).filter(
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.marks.isnot(None)
        ).all()

        assignment_percentages = []

        for submission in submissions:

            assignment = db.query(
                Assignment
            ).filter(
                Assignment.id == submission.assignment_id
            ).first()

            if (
                assignment
                and assignment.max_marks > 0
            ):

                assignment_percentages.append(
                    (
                        submission.marks /
                        assignment.max_marks
                    ) * 100
                )

        assignment_percentage = (
            sum(assignment_percentages) /
            len(assignment_percentages)
            if assignment_percentages
            else 0
        )

        exam_marks = db.query(
            ExamMarks
        ).filter(
            ExamMarks.student_id == student.id
        ).all()

        exam_percentages = []

        for mark in exam_marks:

            exam = db.query(
                Exam
            ).filter(
                Exam.id == mark.exam_id
            ).first()

            if (
                exam
                and exam.max_marks > 0
            ):

                exam_percentages.append(
                    (
                        mark.marks /
                        exam.max_marks
                    ) * 100
                )

        exam_percentage = (
            sum(exam_percentages) /
            len(exam_percentages)
            if exam_percentages
            else 0
        )

        risk = calculate_risk(
            attendance_percentage,
            assignment_percentage,
            exam_percentage
        )

        user = db.query(User).filter(
            User.id == student.user_id
        ).first()

        result.append({
            "student_id": student.id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "roll_number": student.roll_number,
            "department": student.department,
            "year": student.year,
            "section": student.section,
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
        })

    return result


# ============================================================
# ADMIN - RISK SUMMARY
# ============================================================

@app.get("/admin/risk-summary")
def admin_risk_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access risk summary"
        )

    students = db.query(Student).all()

    low = 0
    medium = 0
    high = 0

    for student in students:

        attendance_records = db.query(
            Attendance
        ).filter(
            Attendance.student_id == student.id
        ).all()

        if attendance_records:

            present = sum(
                1
                for record in attendance_records
                if record.status.lower() == "present"
            )

            attendance_percentage = (
                present /
                len(attendance_records)
            ) * 100

        else:

            attendance_percentage = 0

        submissions = db.query(
            AssignmentSubmission
        ).filter(
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.marks.isnot(None)
        ).all()

        assignment_percentages = []

        for submission in submissions:

            assignment = db.query(
                Assignment
            ).filter(
                Assignment.id == submission.assignment_id
            ).first()

            if (
                assignment
                and assignment.max_marks > 0
            ):

                assignment_percentages.append(
                    (
                        submission.marks /
                        assignment.max_marks
                    ) * 100
                )

        assignment_percentage = (
            sum(assignment_percentages) /
            len(assignment_percentages)
            if assignment_percentages
            else 0
        )

        exam_marks = db.query(
            ExamMarks
        ).filter(
            ExamMarks.student_id == student.id
        ).all()

        exam_percentages = []

        for mark in exam_marks:

            exam = db.query(
                Exam
            ).filter(
                Exam.id == mark.exam_id
            ).first()

            if (
                exam
                and exam.max_marks > 0
            ):

                exam_percentages.append(
                    (
                        mark.marks /
                        exam.max_marks
                    ) * 100
                )

        exam_percentage = (
            sum(exam_percentages) /
            len(exam_percentages)
            if exam_percentages
            else 0
        )

        risk = calculate_risk(
            attendance_percentage,
            assignment_percentage,
            exam_percentage
        )

        if risk["risk_level"] == "HIGH":
            high += 1

        elif risk["risk_level"] == "MEDIUM":
            medium += 1

        else:
            low += 1

    return {
        "total_students": len(students),
        "low_risk": low,
        "medium_risk": medium,
        "high_risk": high
    }


# ============================================================
# ADMIN - COURSE PERFORMANCE
# ============================================================

@app.get("/admin/course-performance")
def admin_course_performance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access course performance"
        )

    courses = db.query(Course).all()

    result = []

    for course in courses:

        enrollments = db.query(
            Enrollment
        ).filter(
            Enrollment.course_id == course.id
        ).all()

        student_scores = []

        for enrollment in enrollments:

            student_id = enrollment.student_id

            attendance_records = db.query(
                Attendance
            ).filter(
                Attendance.student_id == student_id,
                Attendance.course_id == course.id
            ).all()

            if attendance_records:

                present = sum(
                    1
                    for record in attendance_records
                    if record.status.lower() == "present"
                )

                attendance_percentage = (
                    present /
                    len(attendance_records)
                ) * 100

            else:

                attendance_percentage = 0

            assignments = db.query(
                Assignment
            ).filter(
                Assignment.course_id == course.id
            ).all()

            assignment_scores = []

            for assignment in assignments:

                submission = db.query(
                    AssignmentSubmission
                ).filter(
                    AssignmentSubmission.assignment_id ==
                    assignment.id,
                    AssignmentSubmission.student_id ==
                    student_id
                ).first()

                if (
                    submission
                    and submission.marks is not None
                    and assignment.max_marks > 0
                ):

                    assignment_scores.append(
                        (
                            submission.marks /
                            assignment.max_marks
                        ) * 100
                    )

            assignment_percentage = (
                sum(assignment_scores) /
                len(assignment_scores)
                if assignment_scores
                else 0
            )

            exams = db.query(Exam).filter(
                Exam.course_id == course.id
            ).all()

            exam_scores = []

            for exam in exams:

                marks = db.query(
                    ExamMarks
                ).filter(
                    ExamMarks.exam_id == exam.id,
                    ExamMarks.student_id == student_id
                ).first()

                if (
                    marks
                    and exam.max_marks > 0
                ):

                    exam_scores.append(
                        (
                            marks.marks /
                            exam.max_marks
                        ) * 100
                    )

            exam_percentage = (
                sum(exam_scores) /
                len(exam_scores)
                if exam_scores
                else 0
            )

            performance = calculate_course_performance(
                attendance_percentage,
                assignment_percentage,
                exam_percentage
            )

            student_scores.append(
                performance["overall_score"]
            )

        average_score = (
            sum(student_scores) /
            len(student_scores)
            if student_scores
            else 0
        )

        result.append({
            "course_id": course.id,
            "course_name": course.name,
            "course_code": course.code,
            "enrolled_students": len(enrollments),
            "average_performance": round(
                average_score,
                2
            )
        })

    result.sort(
        key=lambda x: x["average_performance"]
    )

    return {
        "courses": result,
        "weakest_course": (
            result[0]["course_name"]
            if result
            else None
        ),
        "strongest_course": (
            result[-1]["course_name"]
            if result
            else None
        )
    }


# ============================================================
# ADMIN - OVERALL ANALYTICS
# ============================================================

@app.get("/admin/analytics")
def admin_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access analytics"
        )

    students = db.query(Student).all()

    total_attendance = []
    total_assignment = []
    total_exam = []

    for student in students:

        attendance_records = db.query(
            Attendance
        ).filter(
            Attendance.student_id == student.id
        ).all()

        if attendance_records:

            present = sum(
                1
                for record in attendance_records
                if record.status.lower() == "present"
            )

            attendance = (
                present /
                len(attendance_records)
            ) * 100

            total_attendance.append(attendance)

        submissions = db.query(
            AssignmentSubmission
        ).filter(
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.marks.isnot(None)
        ).all()

        assignment_scores = []

        for submission in submissions:

            assignment = db.query(
                Assignment
            ).filter(
                Assignment.id == submission.assignment_id
            ).first()

            if (
                assignment
                and assignment.max_marks > 0
            ):

                assignment_scores.append(
                    (
                        submission.marks /
                        assignment.max_marks
                    ) * 100
                )

        if assignment_scores:

            total_assignment.append(
                sum(assignment_scores) /
                len(assignment_scores)
            )

        exam_marks = db.query(
            ExamMarks
        ).filter(
            ExamMarks.student_id == student.id
        ).all()

        exam_scores = []

        for mark in exam_marks:

            exam = db.query(
                Exam
            ).filter(
                Exam.id == mark.exam_id
            ).first()

            if (
                exam
                and exam.max_marks > 0
            ):

                exam_scores.append(
                    (
                        mark.marks /
                        exam.max_marks
                    ) * 100
                )

        if exam_scores:

            total_exam.append(
                sum(exam_scores) /
                len(exam_scores)
            )

    return {
        "total_students": len(students),

        "average_attendance": round(
            sum(total_attendance) /
            len(total_attendance)
            if total_attendance
            else 0,
            2
        ),

        "average_assignment_performance": round(
            sum(total_assignment) /
            len(total_assignment)
            if total_assignment
            else 0,
            2
        ),

        "average_exam_performance": round(
            sum(total_exam) /
            len(total_exam)
            if total_exam
            else 0,
            2
        ),

        "total_courses": db.query(Course).count(),

        "total_teachers": db.query(Teacher).count(),

        "total_enrollments": db.query(
            Enrollment
        ).count()
    }


# ============================================================
# ADMIN - STUDENT DETAILS
# ============================================================

@app.get("/admin/students/{student_id}")
def admin_student_details(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access student details"
        )

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    user = db.query(User).filter(
        User.id == student.user_id
    ).first()

    attendance_records = db.query(
        Attendance
    ).filter(
        Attendance.student_id == student.id
    ).all()

    if attendance_records:

        present = sum(
            1
            for record in attendance_records
            if record.status.lower() == "present"
        )

        attendance_percentage = (
            present /
            len(attendance_records)
        ) * 100

    else:

        attendance_percentage = 0

    submissions = db.query(
        AssignmentSubmission
    ).filter(
        AssignmentSubmission.student_id == student.id,
        AssignmentSubmission.marks.isnot(None)
    ).all()

    assignment_scores = []

    for submission in submissions:

        assignment = db.query(
            Assignment
        ).filter(
            Assignment.id == submission.assignment_id
        ).first()

        if (
            assignment
            and assignment.max_marks > 0
        ):

            assignment_scores.append(
                (
                    submission.marks /
                    assignment.max_marks
                ) * 100
            )

    assignment_percentage = (
        sum(assignment_scores) /
        len(assignment_scores)
        if assignment_scores
        else 0
    )

    exam_marks = db.query(
        ExamMarks
    ).filter(
        ExamMarks.student_id == student.id
    ).all()

    exam_scores = []

    for mark in exam_marks:

        exam = db.query(
            Exam
        ).filter(
            Exam.id == mark.exam_id
        ).first()

        if (
            exam
            and exam.max_marks > 0
        ):

            exam_scores.append(
                (
                    mark.marks /
                    exam.max_marks
                ) * 100
            )

    exam_percentage = (
        sum(exam_scores) /
        len(exam_scores)
        if exam_scores
        else 0
    )

    risk = calculate_risk(
        attendance_percentage,
        assignment_percentage,
        exam_percentage
    )

    return {
        "student_id": student.id,
        "name": user.name if user else None,
        "email": user.email if user else None,
        "roll_number": student.roll_number,
        "department": student.department,
        "year": student.year,
        "section": student.section,
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


# ============================================================
# ADMIN - DELETE USER
# ============================================================

@app.delete("/admin/users/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can delete users"
        )

    if current_user.get("user_id") == user_id:

        raise HTTPException(
            status_code=400,
            detail="Admin cannot delete their own account"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    student = db.query(Student).filter(
        Student.user_id == user_id
    ).first()

    teacher = db.query(Teacher).filter(
        Teacher.user_id == user_id
    ).first()

    if student:

        db.delete(student)

    if teacher:

        db.delete(teacher)

    db.delete(user)

    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


# ============================================================
# ADMIN - HEALTH CHECK
# ============================================================

@app.get("/admin/health")
def admin_health(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Only admins can access this endpoint"
        )

    try:

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "api": "running"
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "database": "error",
            "api": "running",
            "error": str(e)
        }