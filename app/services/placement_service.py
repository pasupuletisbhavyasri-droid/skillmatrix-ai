"""
Placement Hub engine: composes existing scores into readiness percentage.
"""
from app.models import Resume, InterviewResult, StudentSkill, Certification, Project

_PLACEMENT_WEIGHTS = {
    "resume": 0.20,
    "interview": 0.25,
    "skills": 0.20,
    "portfolio": 0.15,
    "employability": 0.20,
}


def get_placement_readiness(student) -> dict:
    resume_score = _resume_readiness(student.id)
    interview_score = _interview_readiness(student.id)
    skills_score = _skills_readiness(student.id)
    portfolio_score = _portfolio_readiness(student.id)
    employability_score = student.employability_score or 0.0

    overall = round(
        resume_score * _PLACEMENT_WEIGHTS["resume"]
        + interview_score * _PLACEMENT_WEIGHTS["interview"]
        + skills_score * _PLACEMENT_WEIGHTS["skills"]
        + portfolio_score * _PLACEMENT_WEIGHTS["portfolio"]
        + employability_score * _PLACEMENT_WEIGHTS["employability"],
        1,
    )

    checklist = _build_checklist(student, resume_score, interview_score, skills_score, portfolio_score)

    return {
        "overall_readiness": overall,
        "checklist": checklist,
        "components": {
            "resume": resume_score,
            "interview": interview_score,
            "skills": skills_score,
            "portfolio": portfolio_score,
            "employability": employability_score,
        },
    }


def _resume_readiness(student_id) -> float:
    resume = Resume.query.filter_by(student_id=student_id, is_active=True).first()
    return round(resume.ats_score, 1) if resume else 0.0


def _interview_readiness(student_id) -> float:
    recent = (
        InterviewResult.query.filter_by(student_id=student_id)
        .order_by(InterviewResult.taken_at.desc())
        .limit(3)
        .all()
    )
    if not recent:
        return 0.0
    return round(sum(r.interview_score for r in recent) / len(recent), 1)


def _skills_readiness(student_id) -> float:
    count = StudentSkill.query.filter_by(student_id=student_id).count()
    return round(min(count / 10, 1.0) * 100, 1)


def _portfolio_readiness(student_id) -> float:
    project_count = Project.query.filter_by(student_id=student_id).count()
    cert_count = Certification.query.filter_by(student_id=student_id).count()
    combined = min((project_count / 5.0) + (cert_count / 5.0), 2.0) / 2.0
    return round(combined * 100, 1)


def _build_checklist(student, resume_score, interview_score, skills_score, portfolio_score) -> list:
    return [
        {
            "label": "Resume uploaded & optimized",
            "completed": resume_score >= 60,
            "detail": f"ATS score: {resume_score}%" if resume_score > 0 else "No resume uploaded yet.",
        },
        {
            "label": "Practiced mock interviews",
            "completed": interview_score >= 60,
            "detail": f"Recent avg score: {interview_score}%" if interview_score > 0 else "No interview attempts yet.",
        },
        {
            "label": "Skills profile is strong",
            "completed": skills_score >= 70,
            "detail": f"{skills_score}% of target skill breadth reached.",
        },
        {
            "label": "Portfolio has enough projects/certifications",
            "completed": portfolio_score >= 60,
            "detail": f"{portfolio_score}% portfolio strength.",
        },
        {
            "label": "Employability score is competitive",
            "completed": (student.employability_score or 0) >= 60,
            "detail": f"Current score: {round(student.employability_score or 0, 1)}%.",
        },
    ]
