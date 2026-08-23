"""InterviewQuestion, InterviewResult."""
from datetime import datetime
from app.extensions import db


class InterviewQuestion(db.Model):
    __tablename__ = "interview_questions"

    id = db.Column(db.Integer, primary_key=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # HR/Technical/Behavioral/Coding/Scenario/Problem Solving
    question_text = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default="Medium")
    sample_answer = db.Column(db.Text, nullable=True)
    # Added for the full Interview Hub upgrade — each question now carries
    # enough structure to power a real "explain the answer" experience,
    # not just a score.
    explanation = db.Column(db.Text, nullable=True)          # why the sample answer is strong
    key_points = db.Column(db.Text, nullable=True)             # JSON-encoded list of bullet points
    evaluation_criteria = db.Column(db.Text, nullable=True)    # what a rubric-based grader would look for
    expected_duration_seconds = db.Column(db.Integer, default=90)

    career_role = db.relationship("CareerRole", back_populates="interview_questions")


class InterviewResult(db.Model):
    __tablename__ = "interview_results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=True)
    interview_score = db.Column(db.Float, default=0.0)
    communication_rating = db.Column(db.Float, default=0.0)
    readiness_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text, nullable=True)
    total_duration_seconds = db.Column(db.Integer, default=0)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="interview_results")
    career_role = db.relationship("CareerRole")
