"""
Learning Hub engine: turns skill gaps into a structured learning plan.
"""
import json
from app.models import Course, LearningResource, ProjectIdea
from app.services.skill_gap_service import get_top_skill_gaps_across_interest


def generate_learning_plan(student, target_role=None) -> dict:
    if target_role is None:
        top_matches = get_top_skill_gaps_across_interest(student, limit=1)
        if not top_matches:
            return _empty_plan()
        target_role, analysis = top_matches[0]
    else:
        from app.services.skill_gap_service import calculate_skill_match
        analysis = calculate_skill_match(student, target_role)

    missing = analysis["missing"]

    weekly_goals = []
    for i, skill in enumerate(missing[:6], start=1):
        weekly_goals.append({
            "week_number": i,
            "focus_skill": skill["skill_name"],
            "priority": skill["priority"],
            "tasks": _generate_tasks_for_skill(skill["skill_name"]),
        })

    daily_plan_today = []
    if weekly_goals:
        daily_plan_today = weekly_goals[0]["tasks"][:2]

    return {
        "target_role": target_role,
        "priority_skills": [{"skill_name": s["skill_name"], "priority": s["priority"]} for s in missing],
        "weekly_goals": weekly_goals,
        "daily_plan_today": daily_plan_today,
    }


def _generate_tasks_for_skill(skill_name: str) -> list:
    return [
        f"Watch an introductory tutorial on {skill_name}.",
        f"Complete a small hands-on exercise using {skill_name}.",
        f"Build a mini-project that applies {skill_name}.",
        f"Review and summarize what you learned about {skill_name} in your own words.",
    ]


def _empty_plan() -> dict:
    return {"target_role": None, "priority_skills": [], "weekly_goals": [], "daily_plan_today": []}


def get_recommended_courses(skill_names: list, limit: int = 10):
    if not skill_names:
        return Course.query.limit(limit).all()
    from app.models import Skill
    skill_ids = [s.id for s in Skill.query.filter(Skill.name.in_(skill_names)).all()]
    return Course.query.filter(Course.skill_id.in_(skill_ids)).limit(limit).all()


def get_project_ideas_for_role(career_role, limit: int = 10):
    return ProjectIdea.query.filter_by(career_role_id=career_role.id).limit(limit).all()


def get_role_learning_resources_grouped(career_role) -> dict:
    """
    Parses CareerRole.learning_resources (JSON list of {title, type, url})
    and groups by type — this is the "Courses, Books, YouTube,
    Documentation, Certifications" content the Learning Hub surfaces per
    role, seeded alongside each career (see data/seed/career_roles.json).
    """
    if not career_role.learning_resources:
        return {}

    try:
        items = json.loads(career_role.learning_resources)
    except (ValueError, TypeError):
        return {}

    grouped = {}
    for item in items:
        rtype = item.get("type", "Other")
        grouped.setdefault(rtype, []).append(item)

    # Fold in required_certifications as a "Certifications" group too, since
    # that's a distinct field on CareerRole but conceptually the same
    # "what to go learn/earn next" content the Learning Hub shows.
    if career_role.required_certifications:
        try:
            certs = json.loads(career_role.required_certifications)
            if certs:
                grouped["Certification"] = [{"title": c, "type": "Certification", "url": ""} for c in certs]
        except (ValueError, TypeError):
            pass

    return grouped
