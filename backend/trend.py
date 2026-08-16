def calculate_trend(scores):

    # Need at least 2 scores to calculate a trend
    if len(scores) < 2:
        return {
            "trend": "INSUFFICIENT_DATA",
            "recent_average": round(scores[-1], 2) if scores else 0,
            "previous_average": 0,
            "difference": 0
        }

    # Split scores into previous and recent
    middle = len(scores) // 2

    previous_scores = scores[:middle]
    recent_scores = scores[middle:]

    previous_average = (
        sum(previous_scores) / len(previous_scores)
    )

    recent_average = (
        sum(recent_scores) / len(recent_scores)
    )

    difference = recent_average - previous_average

    # Trend rules
    if difference >= 5:
        trend = "IMPROVING"

    elif difference <= -5:
        trend = "DECLINING"

    else:
        trend = "STABLE"

    return {
        "trend": trend,
        "recent_average": round(recent_average, 2),
        "previous_average": round(previous_average, 2),
        "difference": round(difference, 2)
    }