"""
Skill Gap Analysis blueprint.
"""
from flask import render_template, request
from flask_login import login_required, current_user

from app.blueprints.skill_gap import skill_gap_bp
from app.utils.decorators import student_required
from app.models import CareerRole
from app.services.skill_gap_service import calculate_skill_match, get_top_skill_gaps_across_interest


@skill_gap_bp.route("/")
@login_required
@student_required
def index():
    role_slug = request.args.get("role_slug")

    if role_slug:
        role = CareerRole.query.filter_by(slug=role_slug, is_active=True).first_or_404()
        analysis = calculate_skill_match(current_user, role)
        return render_template("skill_gap/detail.html", role=role, analysis=analysis)

    top_matches = get_top_skill_gaps_across_interest(current_user, limit=8)
    return render_template("skill_gap/overview.html", top_matches=top_matches)
