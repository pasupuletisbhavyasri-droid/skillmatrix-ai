"""
Mock Interview Hub.
"""

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from flask_login import login_required, current_user

from app.blueprints.interview_hub import interview_hub_bp
from app.utils.decorators import student_required
from app.models import CareerRole, InterviewQuestion, InterviewResult
from app.services.interview_service import (
    get_interview_question_set,
    submit_interview_session,
)


@interview_hub_bp.route("/")
@login_required
@student_required
def index():
    careers = (
        CareerRole.query
        .filter_by(is_active=True)
        .order_by(CareerRole.title)
        .all()
    )

    history = (
        InterviewResult.query
        .filter_by(student_id=current_user.id)
        .order_by(InterviewResult.taken_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "interview_hub/index.html",
        careers=careers,
        history=history,
    )


@interview_hub_bp.route("/start", methods=["POST"])
@login_required
@student_required
def start():

    role_id = request.form.get("career_role_id", type=int)
    question_type = request.form.get("question_type") or None

    # -----------------------------------------
    # Validate career role
    # -----------------------------------------
    if not role_id:
        flash("Please select a career role.", "warning")
        return redirect(url_for("interview_hub.index"))

    role = CareerRole.query.get_or_404(role_id)

    # -----------------------------------------
    # Get interview questions
    # -----------------------------------------
    questions = get_interview_question_set(
        role,
        question_type=question_type,
        limit=5,
    )

    if not questions:
        flash(
            "No interview questions available for this career yet.",
            "warning",
        )
        return redirect(url_for("interview_hub.index"))

    # -----------------------------------------
    # Save interview session
    # -----------------------------------------
    session["interview_role_id"] = role.id
    session["interview_question_ids"] = [
        q.id for q in questions
    ]

    # Force Flask to save session
    session.modified = True

    return render_template(
        "interview_hub/session.html",
        role=role,
        questions=questions,
    )


@interview_hub_bp.route("/submit", methods=["POST"])
@login_required
@student_required
def submit():

    # -----------------------------------------
    # Get interview session
    # -----------------------------------------
    role_id = session.get("interview_role_id")
    question_ids = session.get("interview_question_ids")

    if not role_id or not question_ids:
        flash(
            "Your interview session expired. Please start the interview again.",
            "warning",
        )
        return redirect(url_for("interview_hub.index"))

    # -----------------------------------------
    # Get career role
    # -----------------------------------------
    role = CareerRole.query.get(role_id)

    if not role:
        session.pop("interview_role_id", None)
        session.pop("interview_question_ids", None)

        flash(
            "The selected career role could not be found.",
            "danger",
        )
        return redirect(url_for("interview_hub.index"))

    # -----------------------------------------
    # Collect answers
    # -----------------------------------------
    answers = []

    for qid in question_ids:

        question = InterviewQuestion.query.get(qid)

        if not question:
            continue

        answer_text = request.form.get(
            f"answer_{qid}",
            ""
        )

        answers.append(
            {
                "question": question,
                "answer_text": answer_text.strip(),
            }
        )

    # -----------------------------------------
    # Make sure questions exist
    # -----------------------------------------
    if not answers:
        flash(
            "No interview answers were received. Please try again.",
            "warning",
        )
        return redirect(
            url_for(
                "interview_hub.start"
            )
        )

    # -----------------------------------------
    # Interview duration
    # -----------------------------------------
    total_duration_seconds = request.form.get(
        "total_duration_seconds",
        default=0,
        type=int,
    )

    if total_duration_seconds is None:
        total_duration_seconds = 0

    # Prevent negative duration
    total_duration_seconds = max(
        0,
        total_duration_seconds
    )

    # -----------------------------------------
    # Evaluate interview
    # -----------------------------------------
    try:

        result = submit_interview_session(
            current_user,
            role,
            answers,
            total_duration_seconds=total_duration_seconds,
        )

    except Exception as exc:

        # Rollback database transaction if something failed
        from app.extensions import db

        db.session.rollback()

        print("\n================ INTERVIEW SUBMIT ERROR ================")
        print(type(exc).__name__, ":", str(exc))
        print("=========================================================\n")

        flash(
            "There was a problem evaluating your interview. "
            "Please try again.",
            "danger",
        )

        return redirect(
            url_for("interview_hub.index")
        )

    # -----------------------------------------
    # Clear interview session
    # -----------------------------------------
    session.pop("interview_role_id", None)
    session.pop("interview_question_ids", None)

    session.modified = True

    # -----------------------------------------
    # Show result
    # -----------------------------------------
    return render_template(
        "interview_hub/result.html",
        role=role,
        result=result,
    )