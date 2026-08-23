"""
Practice Hub: aptitude/technical/programming quizzes with score history,
categories, daily/weekly challenges, and a leaderboard.
"""
import json
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.practice_hub import practice_hub_bp
from app.utils.decorators import student_required
from app.extensions import db
from app.models import Quiz, QuizResult, Student


@practice_hub_bp.route("/")
@login_required
@student_required
def index():
    category = request.args.get("category", "").strip()

    query = Quiz.query
    if category:
        query = query.filter_by(category=category)
    quizzes = query.order_by(Quiz.category).all()

    categories = [row[0] for row in db.session.query(Quiz.category).distinct().order_by(Quiz.category)]

    daily_challenge = Quiz.query.filter_by(is_daily_challenge=True).first()
    weekly_challenge = Quiz.query.filter_by(is_weekly_challenge=True).first()

    history = (
        QuizResult.query.filter_by(student_id=current_user.id)
        .order_by(QuizResult.taken_at.desc())
        .limit(10)
        .all()
    )

    # Progress tracking: % correct over the student's last 10 attempts, oldest first
    progress_history = list(reversed(history))
    progress_labels = [r.taken_at.strftime("%b %d") for r in progress_history]
    progress_scores = [round((r.score / r.total_questions) * 100, 1) if r.total_questions else 0 for r in progress_history]

    return render_template(
        "practice_hub/index.html", quizzes=quizzes, history=history, categories=categories,
        category=category, daily_challenge=daily_challenge, weekly_challenge=weekly_challenge,
        progress_labels=progress_labels, progress_scores=progress_scores,
    )


@practice_hub_bp.route("/<int:quiz_id>/take", methods=["GET", "POST"])
@login_required
@student_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = json.loads(quiz.questions_json)

    if request.method == "POST":
        score = 0
        weak_topics = []
        for i, q in enumerate(questions):
            submitted = request.form.get(f"q{i}")
            if submitted == q.get("answer"):
                score += 1
            else:
                weak_topics.append(q.get("topic", q.get("question", "")[:40]))

        result = QuizResult(
            student_id=current_user.id, quiz_id=quiz.id,
            score=score, total_questions=len(questions),
            weak_topics=json.dumps(weak_topics),
        )
        db.session.add(result)
        db.session.commit()
        flash(f"You scored {score}/{len(questions)}!", "success")
        return redirect(url_for("practice_hub.index"))

    return render_template("practice_hub/take_quiz.html", quiz=quiz, questions=questions)


@practice_hub_bp.route("/leaderboard")
@login_required
@student_required
def leaderboard():
    """
    Ranks students by total quiz points (sum of all QuizResult.score across
    all attempts) — a simple, transparent leaderboard metric that rewards
    both accuracy and practice volume.
    """
    rows = (
        db.session.query(
            Student.id, Student.name, Student.photo_url,
            db.func.sum(QuizResult.score).label("total_points"),
            db.func.count(QuizResult.id).label("attempts"),
        )
        .join(QuizResult, QuizResult.student_id == Student.id)
        .group_by(Student.id)
        .order_by(db.desc("total_points"))
        .limit(20)
        .all()
    )

    my_rank = None
    for i, row in enumerate(rows, start=1):
        if row.id == current_user.id:
            my_rank = i
            break

    return render_template("practice_hub/leaderboard.html", rows=rows, my_rank=my_rank)
