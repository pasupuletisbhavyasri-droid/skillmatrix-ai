"""AI Career Recommendation blueprint."""

import json

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.recommendation import recommendation_bp
from app.utils.decorators import student_required
from app.models import Recommendation
from app.services.recommendation_service import generate_recommendations
from app.services.skill_gap_service import calculate_skill_match


def _safe_json_list(raw):
    """Safely convert a JSON string into a Python list."""

    if not raw:
        return []

    try:
        value = json.loads(raw)

        if isinstance(value, list):
            return value

        return []

    except (ValueError, TypeError, json.JSONDecodeError):
        return []


@recommendation_bp.route("/")
@login_required
@student_required
def index():
    """
    Display the student's current career recommendations.
    """

    latest_batch = (
        Recommendation.query
        .filter_by(student_id=current_user.id)
        .order_by(Recommendation.match_score.desc())
        .all()
    )

    enriched = []

    for rec in latest_batch:

        role = rec.career_role

        # Calculate current skill match
        skill_match = calculate_skill_match(
            current_user,
            role
        )

        enriched.append({
            "rec": rec,
            "role": role,
            "skill_match": skill_match,

            "required_certifications": _safe_json_list(
                role.required_certifications
            ),

            "required_exams": _safe_json_list(
                role.required_exams
            ),

            "companies_hiring": _safe_json_list(
                role.companies_hiring
            ),
        })

    return render_template(
        "recommendation/index.html",
        recommendations=enriched
    )


@recommendation_bp.route("/generate", methods=["POST"])
@login_required
@student_required
def generate():
    """
    Generate a fresh set of personalized career recommendations.
    """

    # Check whether student has added skills
    if not current_user.skills:

        flash(
            "Add some skills to your profile first for better recommendations.",
            "warning"
        )

        return redirect(
            url_for("profile.index")
        )

    try:

        # Generate top 5 recommendations
        generate_recommendations(
            current_user,
            top_n=5,
            persist=True
        )

        flash(
            "Your career recommendations have been refreshed!",
            "success"
        )

    except Exception as exc:

        flash(
            f"Unable to generate recommendations: {exc}",
            "danger"
        )

    return redirect(
        url_for("recommendation.index")
    )