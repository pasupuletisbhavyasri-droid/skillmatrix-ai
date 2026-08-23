"""
Employability Score engine.
"""
from flask import current_app
from app.extensions import db
from app.models import StudentSkill, Project, Certification, Resume

_SKILL_COUNT_CAP = 10
_PROJECT_COUNT_CAP = 5
_CERT_COUNT_CAP = 5


def calculate_employability_score(student) -> dict:
    weights = current_app.config["EMPLOYABILITY_WEIGHTS"]

    cgpa_score = _score_cgpa(student.cgpa)
    skills_score = _score_skills(student.id)
    projects_score = _score_projects(student.id)
    certs_score = _score_certifications(student.id)
    resume_score = _score_resume(student.id)
    communication_score = _score_communication(student.communication_skill_rating)

    weighted_total = (
        cgpa_score * (weights["cgpa"] / 100)
        + skills_score * (weights["technical_skills"] / 100)
        + projects_score * (weights["projects"] / 100)
        + certs_score * (weights["certifications"] / 100)
        + resume_score * (weights["resume"] / 100)
        + communication_score * (weights["communication"] / 100)
    )

    return {
        "overall_score": round(weighted_total, 1),
        "components": {
            "cgpa": {"score": cgpa_score, "weight": weights["cgpa"]},
            "technical_skills": {"score": skills_score, "weight": weights["technical_skills"]},
            "projects": {"score": projects_score, "weight": weights["projects"]},
            "certifications": {"score": certs_score, "weight": weights["certifications"]},
            "resume": {"score": resume_score, "weight": weights["resume"]},
            "communication": {"score": communication_score, "weight": weights["communication"]},
        },
        "suggestions": _generate_suggestions(cgpa_score, skills_score, projects_score, certs_score, resume_score, communication_score),
    }


def recalculate_and_save(student) -> float:
    result = calculate_employability_score(student)
    student.employability_score = result["overall_score"]
    db.session.commit()
    return result["overall_score"]


def _score_cgpa(cgpa) -> float:
    if not cgpa:
        return 0.0
    return round(min(cgpa / 10.0, 1.0) * 100, 1)


def _score_skills(student_id) -> float:
    count = StudentSkill.query.filter_by(student_id=student_id).count()
    return round(min(count / _SKILL_COUNT_CAP, 1.0) * 100, 1)


def _score_projects(student_id) -> float:
    count = Project.query.filter_by(student_id=student_id).count()
    return round(min(count / _PROJECT_COUNT_CAP, 1.0) * 100, 1)


def _score_certifications(student_id) -> float:
    count = Certification.query.filter_by(student_id=student_id).count()
    return round(min(count / _CERT_COUNT_CAP, 1.0) * 100, 1)


def _score_resume(student_id) -> float:
    resume = Resume.query.filter_by(student_id=student_id, is_active=True).first()
    return round(resume.ats_score, 1) if resume else 0.0


def _score_communication(rating) -> float:
    if not rating:
        return 0.0
    return round(min(rating / 10.0, 1.0) * 100, 1)


def _generate_suggestions(cgpa, skills, projects, certs, resume, comm) -> list:
    components = [
        ("CGPA", cgpa, "Focus on improving your academic performance where possible."),
        ("Technical Skills", skills, "Add more skills to your profile — aim for at least 10 relevant technical skills."),
        ("Projects", projects, "Build and document more projects — aim for at least 5 solid projects."),
        ("Certifications", certs, "Earn relevant certifications in your area of interest."),
        ("Resume", resume, "Upload and optimize your resume in the Resume Center for a better ATS score."),
        ("Communication", comm, "Practice mock interviews to improve your communication rating."),
    ]
    weakest = sorted(components, key=lambda c: c[1])[:3]
    return [{"component": name, "score": score, "suggestion": tip} for name, score, tip in weakest if score < 80]
