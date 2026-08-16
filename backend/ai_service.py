from google import genai
import os

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_ai_recommendation(
    attendance,
    assignment_performance,
    exam_performance,
    risk_score,
    risk_level,
    reasons,
    strongest_course,
    weakest_course,
    trend
):

    prompt = f"""
You are an academic recommendation assistant.

Student performance:

Attendance: {attendance}%

Assignment Performance: {assignment_performance}%

Exam Performance: {exam_performance}%

Risk Score: {risk_score}

Risk Level: {risk_level}

Reasons:
{reasons}

Strongest Course:
{strongest_course}

Weakest Course:
{weakest_course}

Performance Trend:
{trend}

Give practical academic recommendations for this student.

Include:
1. Main problem
2. What the student should improve
3. Study recommendations
4. Course-specific recommendation
5. Attendance recommendation
6. Exam/assignment recommendation

Keep the response clear and concise.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text