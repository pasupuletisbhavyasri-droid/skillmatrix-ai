"""
Communication Analysis blueprint. Improves (does not remove) the
existing communication_skill_rating field — this module is the "how"
behind that number: a structured self-assessment, a computed 0-100
score, strengths/weaknesses, suggestions, and an improvement roadmap.
"""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.communication import communication_bp
from app.utils.decorators import student_required
from app.blueprints.communication.forms import CommunicationAssessmentForm
from app.services.communication_service import (
    submit_assessment, get_latest_assessment, get_assessment_history,
)


@communication_bp.route("/", methods=["GET", "POST"])
@login_required
@student_required
def index():
    form = CommunicationAssessmentForm()

    if form.validate_on_submit():
        ratings = {
            "speaking_skills": form.speaking_skills.data,
            "english_communication": form.english_communication.data,
            "grammar": form.grammar.data,
            "vocabulary": form.vocabulary.data,
            "pronunciation": form.pronunciation.data,
            "fluency": form.fluency.data,
            "confidence": form.confidence.data,
            "presentation_skills": form.presentation_skills.data,
            "teamwork": form.teamwork.data,
            "leadership": form.leadership.data,
            "problem_solving": form.problem_solving.data,
        }
        assessment = submit_assessment(current_user, ratings)
        flash("Communication analysis complete!", "success")
        return redirect(url_for("communication.result", assessment_id=assessment.id))

    latest = get_latest_assessment(current_user)
    history = get_assessment_history(current_user)
    return render_template("communication/index.html", form=form, latest=latest, history=history)


@communication_bp.route("/<int:assessment_id>")
@login_required
@student_required
def result(assessment_id):
    import json
    from app.models import CommunicationAssessment

    assessment = CommunicationAssessment.query.filter_by(
        id=assessment_id, student_id=current_user.id
    ).first_or_404()

    strengths = json.loads(assessment.strengths) if assessment.strengths else []
    weaknesses = json.loads(assessment.weaknesses) if assessment.weaknesses else []
    suggestions = json.loads(assessment.suggestions) if assessment.suggestions else []
    roadmap = json.loads(assessment.roadmap) if assessment.roadmap else []

    return render_template(
        "communication/result.html", assessment=assessment,
        strengths=strengths, weaknesses=weaknesses, suggestions=suggestions, roadmap=roadmap,
    )
