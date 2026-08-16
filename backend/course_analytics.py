def calculate_course_performance(
    attendance_percentage,
    assignment_percentage,
    exam_percentage
):
    """
    Calculate overall performance for one course.

    Weight:
    Attendance   = 20%
    Assignments  = 30%
    Exams        = 50%
    """

    overall_score = (
        attendance_percentage * 0.20
        + assignment_percentage * 0.30
        + exam_percentage * 0.50
    )

    if overall_score >= 75:
        performance = "GOOD"

    elif overall_score >= 60:
        performance = "AVERAGE"

    else:
        performance = "WEAK"

    return {
        "attendance": round(attendance_percentage, 2),
        "assignment_performance": round(
            assignment_percentage, 2
        ),
        "exam_performance": round(
            exam_percentage, 2
        ),
        "overall_score": round(
            overall_score, 2
        ),
        "performance": performance
    }