"""
Skill Gap Analysis engine.
"""
from app.models import StudentSkill, CareerSkill

_LEARN_WEEKS_BY_PRIORITY = {"High": 3, "Medium": 2, "Low": 1}
_PRIORITY_WEIGHT = {"High": 3, "Medium": 2, "Low": 1}


def calculate_skill_match(student, career_role) -> dict:
    student_skill_names = {
        link.skill.name.lower(): link.proficiency_level
        for link in StudentSkill.query.filter_by(student_id=student.id).all()
    }

    required_skills = CareerSkill.query.filter_by(career_role_id=career_role.id).all()

    matched = []
    missing = []
    total_weight = 0
    matched_weight = 0

    for req in required_skills:
        weight = _PRIORITY_WEIGHT.get(req.priority, 2)
        total_weight += weight
        skill_name_lower = req.skill.name.lower()

        if skill_name_lower in student_skill_names:
            matched_weight += weight
            matched.append({
                "skill_name": req.skill.name,
                "priority": req.priority,
                "student_level": student_skill_names[skill_name_lower],
            })
        else:
            missing.append({
                "skill_name": req.skill.name,
                "priority": req.priority,
                "required_level": req.required_level,
            })

    match_percentage = round((matched_weight / total_weight) * 100, 1) if total_weight > 0 else 0.0

    missing.sort(key=lambda s: _PRIORITY_WEIGHT.get(s["priority"], 0), reverse=True)

    estimated_weeks = sum(_LEARN_WEEKS_BY_PRIORITY.get(s["priority"], 2) for s in missing)

    return {
        "match_percentage": match_percentage,
        "matched": matched,
        "missing": missing,
        "estimated_learning_weeks": estimated_weeks,
    }


def get_top_skill_gaps_across_interest(student, limit: int = 5):
    from app.models import CareerRole

    roles = CareerRole.query.filter_by(is_active=True).all()
    scored = [(role, calculate_skill_match(student, role)) for role in roles]
    scored.sort(key=lambda pair: pair[1]["match_percentage"], reverse=True)
    return scored[:limit]
