"""Quiz and QuizResult — Practice Hub."""
from datetime import datetime
from app.extensions import db


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default="Medium")
    questions_json = db.Column(db.Text, nullable=False)
    # Practice Hub challenge flags — a quiz can be flagged as the current
    # daily or weekly challenge (admin-set); index page highlights these.
    is_daily_challenge = db.Column(db.Boolean, default=False)
    is_weekly_challenge = db.Column(db.Boolean, default=False)

    results = db.relationship("QuizResult", back_populates="quiz", cascade="all, delete-orphan")


class QuizResult(db.Model):
    __tablename__ = "quiz_results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    weak_topics = db.Column(db.Text, nullable=True)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="quiz_results")
    quiz = db.relationship("Quiz", back_populates="results")
