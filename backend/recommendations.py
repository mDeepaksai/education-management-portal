def generate_recommendations(
    attendance,
    assignment_performance,
    exam_performance,
    risk_level,
    trend,
    strongest_course=None,
    weakest_course=None
):
    recommendations = []

    # Attendance
    if attendance < 75:
        recommendations.append(
            "Improve your attendance. Aim to maintain at least 75% attendance."
        )
    else:
        recommendations.append(
            "Your attendance is satisfactory. Continue attending classes regularly."
        )

    # Assignment performance
    if assignment_performance < 60:
        recommendations.append(
            "Focus more on assignments and complete them on time."
        )
    elif assignment_performance < 75:
        recommendations.append(
            "Improve your assignment performance by reviewing mistakes and practicing more."
        )
    else:
        recommendations.append(
            "Your assignment performance is good. Continue maintaining this level."
        )

    # Exam performance
    if exam_performance < 60:
        recommendations.append(
            "Your examination performance is weak. Increase your revision and practice time."
        )
    elif exam_performance < 75:
        recommendations.append(
            "Your examination performance needs improvement. Practice more questions before exams."
        )
    else:
        recommendations.append(
            "Your examination performance is good. Continue your current preparation."
        )

    # Trend
    if trend == "DECLINING":
        recommendations.append(
            "Your recent performance is declining. Review recent topics and increase study time."
        )
    elif trend == "IMPROVING":
        recommendations.append(
            "Your performance is improving. Continue following your current study routine."
        )
    elif trend == "STABLE":
        recommendations.append(
            "Your performance is stable. Focus on gradually improving your weaker areas."
        )

    # Risk
    if risk_level == "HIGH":
        recommendations.append(
            "Your academic risk is high. Prioritize weak subjects and create a consistent study schedule."
        )
    elif risk_level == "MEDIUM":
        recommendations.append(
            "Your academic risk is moderate. Address weak areas before your performance declines further."
        )
    else:
        recommendations.append(
            "Your academic risk is low. Continue maintaining consistent academic performance."
        )

    # Weakest course
    if weakest_course:
        recommendations.append(
            f"Give additional attention to {weakest_course}, as it is currently your weakest course."
        )

    # Strongest course
    if strongest_course:
        recommendations.append(
            f"Continue maintaining your performance in {strongest_course}, which is currently your strongest course."
        )

    return {
        "risk_level": risk_level,
        "trend": trend,
        "strongest_course": strongest_course,
        "weakest_course": weakest_course,
        "recommendations": recommendations
    }