def calculate_admin_status(overall_score):
    if overall_score >= 75:
        return "GOOD"
    elif overall_score >= 60:
        return "AVERAGE"
    else:
        return "NEEDS_IMPROVEMENT"