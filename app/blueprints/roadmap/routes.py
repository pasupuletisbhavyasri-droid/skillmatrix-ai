"""
Personalized Learning Roadmap.

Displays the student's career-based skill roadmap.
"""

from flask import render_template
from flask_login import login_required, current_user

from app.blueprints.roadmap import roadmap_bp
from app.models import CareerRole, CareerSkill


@roadmap_bp.route("/")
@login_required
def index():
    """
    Display the personalized learning roadmap
    for the logged-in student.
    """

    student = current_user

    career_interest = getattr(
        student,
        "career_interest",
        None
    )

    career = None

    # Try to find the student's selected career.
    if career_interest:
        career = (
            CareerRole.query
            .filter(
                CareerRole.is_active.is_(True),
                CareerRole.title.ilike(
                    f"%{career_interest}%"
                )
            )
            .first()
        )

    # Fallback to Full Stack Developer if
    # the student's career cannot be found.
    if not career:
        career = (
            CareerRole.query
            .filter(
                CareerRole.is_active.is_(True),
                CareerRole.title.ilike("%Full Stack%")
            )
            .first()
        )

    # Final fallback to any active career.
    if not career:
        career = (
            CareerRole.query
            .filter_by(is_active=True)
            .first()
        )

    required_skills = []

    if career:
        required_skills = (
            CareerSkill.query
            .filter_by(
                career_role_id=career.id
            )
            .order_by(
                CareerSkill.priority.desc()
            )
            .all()
        )

    # Current student skills
    current_skill_names = set()

    try:
        for student_skill in student.skills:

            skill = getattr(
                student_skill,
                "skill",
                None
            )

            if skill and skill.name:
                current_skill_names.add(
                    skill.name.strip().lower()
                )

    except Exception:
        current_skill_names = set()

    # Calculate missing skills
    missing_skills = []

    for career_skill in required_skills:

        skill = career_skill.skill

        if not skill:
            continue

        skill_name = skill.name.strip()

        if skill_name.lower() not in current_skill_names:
            missing_skills.append(
                career_skill
            )

    total_required = len(required_skills)
    total_missing = len(missing_skills)

    if total_required:
        completed_count = (
            total_required - total_missing
        )

        progress = round(
            (completed_count / total_required) * 100,
            1
        )

    else:
        progress = 0

    return render_template(
        "roadmap/index.html",
        student=student,
        career=career,
        required_skills=required_skills,
        missing_skills=missing_skills,
        total_required=total_required,
        total_missing=total_missing,
        progress=progress
    )