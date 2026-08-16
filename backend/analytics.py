def calculate_risk(attendance, assignment, exam):

    risk_score = 0
    reasons = []

    # Attendance
    if attendance < 75:
        risk_score += 30
        reasons.append("Low attendance")

    # Assignment
    if assignment < 60:
        risk_score += 30
        reasons.append("Low assignment performance")

    # Exam
    if exam < 60:
        risk_score += 40
        reasons.append("Low examination performance")

    # Risk level
    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons
    }