"""
Rule-based Career Recommendation engine.
"""
import json
from datetime import datetime
from app.extensions import db
from app.models import CareerRole, Recommendation, Project, Certification
from app.services.skill_gap_service import calculate_skill_match

_RECOMMENDATION_WEIGHTS = {
    "skill_match": 0.40,
    "interest_match": 0.20,
    "cgpa_fit": 0.10,
    "portfolio_strength": 0.15,
    "employability_alignment": 0.15,
}


def generate_recommendations(student, top_n: int = 5, persist: bool = True) -> list:
    roles = CareerRole.query.filter_by(is_active=True).all()
    scored = []

    portfolio_strength = _score_portfolio_strength(student.id)

    for role in roles:
        skill_result = calculate_skill_match(student, role)
        skill_score = skill_result["match_percentage"]

        interest_score = _score_interest_match(student.career_interest, role)
        cgpa_score = _score_cgpa_fit(student.cgpa, role)
        employability_score = _score_employability_alignment(student.employability_score, role)

        total = (
            skill_score * _RECOMMENDATION_WEIGHTS["skill_match"]
            + interest_score * _RECOMMENDATION_WEIGHTS["interest_match"]
            + cgpa_score * _RECOMMENDATION_WEIGHTS["cgpa_fit"]
            + portfolio_strength * _RECOMMENDATION_WEIGHTS["portfolio_strength"]
            + employability_score * _RECOMMENDATION_WEIGHTS["employability_alignment"]
        )

        reason = _build_reason(skill_score, interest_score, skill_result)

        # roles are iterated once here, so `scored` can never contain the
        # same career_role twice within a batch — this, plus clearing the
        # student's prior batch in _persist_recommendations below, is what
        # "prevent duplicate recommendations" means in practice.
        scored.append({
            "career_role": role,
            "total_score": round(total, 1),
            "reason": reason,
            "skill_match": skill_result,
            "required_certifications": _safe_json_list(role.required_certifications),
            "required_exams": _safe_json_list(role.required_exams),
            "companies_hiring": _safe_json_list(role.companies_hiring),
            "career_growth": role.career_growth,
            "estimated_learning_weeks": skill_result["estimated_learning_weeks"],
        })

    scored.sort(key=lambda item: item["total_score"], reverse=True)
    top_results = scored[:top_n]

    if persist:
        _persist_recommendations(student, top_results)

    return top_results


def _safe_json_list(raw) -> list:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return []


def _score_interest_match(career_interest: str, role: CareerRole) -> float:
    if not career_interest:
        return 50.0

    interest_lower = career_interest.lower()
    role_text = f"{role.title} {role.category}".lower()

    if interest_lower in role_text or role.category.lower() in interest_lower:
        return 100.0

    interest_words = set(interest_lower.split())
    role_words = set(role_text.split())
    overlap = interest_words & role_words
    if overlap:
        return 65.0

    return 30.0


def _score_cgpa_fit(cgpa, role: CareerRole) -> float:
    if not cgpa:
        return 50.0

    base = min(cgpa / 10.0, 1.0) * 100
    if role.industry_demand_score and role.industry_demand_score > 85:
        return base
    return max(base, 70.0)


def _score_portfolio_strength(student_id) -> float:
    project_count = Project.query.filter_by(student_id=student_id).count()
    cert_count = Certification.query.filter_by(student_id=student_id).count()
    combined = min((project_count / 5.0) + (cert_count / 5.0), 2.0) / 2.0
    return round(combined * 100, 1)


def _score_employability_alignment(employability_score, role: CareerRole) -> float:
    if employability_score is None:
        return 50.0

    demand = role.industry_demand_score or 50.0
    gap = abs(employability_score - demand)
    return max(0.0, 100.0 - gap)


def _build_reason(skill_score, interest_score, skill_result) -> str:
    parts = []
    if skill_score >= 70:
        parts.append(f"strong skill match ({skill_score}%)")
    elif skill_score >= 40:
        parts.append(f"partial skill match ({skill_score}%)")

    if interest_score >= 90:
        parts.append("aligns with your stated career interest")

    if skill_result["matched"]:
        top_matched = ", ".join(s["skill_name"] for s in skill_result["matched"][:2])
        parts.append(f"you already have {top_matched}")

    if not parts:
        return "Worth exploring based on your overall profile."

    return "Recommended because of " + "; ".join(parts) + "."


def _persist_recommendations(student, results) -> None:
    """
    Clears the student's previous recommendation batch before saving the
    new one — prevents duplicate/stale rows for the same career piling up
    every time a student clicks "Refresh Recommendations", and guarantees
    the Recommendation Report and admin analytics always reflect the
    latest, non-duplicated set.
    """
    Recommendation.query.filter_by(student_id=student.id).delete()

    for item in results:
        db.session.add(Recommendation(
            student_id=student.id,
            career_role_id=item["career_role"].id,
            match_score=item["total_score"],
            reason=item["reason"],
            generated_at=datetime.utcnow(),
        ))
    db.session.commit()
