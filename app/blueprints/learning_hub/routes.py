"""Learning Hub: personalized roadmap, courses, project ideas."""
from flask import render_template, request
from flask_login import login_required, current_user

from app.blueprints.learning_hub import learning_hub_bp
from app.utils.decorators import student_required
from app.models import CareerRole
from app.services.learning_service import (
    generate_learning_plan, get_recommended_courses, get_project_ideas_for_role,
    get_role_learning_resources_grouped,
)


@learning_hub_bp.route("/")
@login_required
@student_required
def index():
    role_slug = request.args.get("role_slug")
    target_role = CareerRole.query.filter_by(slug=role_slug).first() if role_slug else None

    plan = generate_learning_plan(current_user, target_role=target_role)

    courses = []
    project_ideas = []
    resources_grouped = {}
    if plan["target_role"]:
        skill_names = [s["skill_name"] for s in plan["priority_skills"]]
        courses = get_recommended_courses(skill_names, limit=8)
        project_ideas = get_project_ideas_for_role(plan["target_role"], limit=6)
        resources_grouped = get_role_learning_resources_grouped(plan["target_role"])

    all_careers = CareerRole.query.filter_by(is_active=True).order_by(CareerRole.title).all()

    return render_template(
        "learning_hub/index.html",
        plan=plan, courses=courses, project_ideas=project_ideas, all_careers=all_careers,
        resources_grouped=resources_grouped,
    )
