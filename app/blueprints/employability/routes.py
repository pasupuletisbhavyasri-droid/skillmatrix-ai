"""Employability Score breakdown page."""
from flask import render_template
from flask_login import login_required, current_user

from app.blueprints.employability import employability_bp
from app.utils.decorators import student_required
from app.utils.helpers import cgpa_category
from app.services.employability_service import calculate_employability_score, recalculate_and_save


@employability_bp.route("/")
@login_required
@student_required
def index():
    recalculate_and_save(current_user)
    breakdown = calculate_employability_score(current_user)
    cgpa_info = cgpa_category(current_user.cgpa)
    return render_template("employability/index.html", breakdown=breakdown, cgpa_info=cgpa_info)
