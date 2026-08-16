def calculate_student_status(
    attendance,
    assignment_performance,
    exam_performance
):
    overall_score = (
        attendance * 0.20
        + assignment_performance * 0.30
        + exam_performance * 0.50
    )

    if overall_score >= 75:
        status = "GOOD"
    elif overall_score >= 60:
        status = "AVERAGE"
    else:
        status = "NEEDS_IMPROVEMENT"

    return {
        "overall_score": round(overall_score, 2),
        "status": status
    }