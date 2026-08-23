"""
CommunicationAssessment — stores each self-assessment a student submits
for the Communication Analysis module. History-preserving (like
Recommendation and InterviewResult) so a student can see improvement
over time, and so Employability/Dashboard/Reports can read the latest one.
"""
from datetime import datetime
from app.extensions import db


class CommunicationAssessment(db.Model):
    __tablename__ = "communication_assessments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)

    # Raw 0-10 self-ratings across the dimensions your spec lists
    speaking_skills = db.Column(db.Float, default=0.0)
    english_communication = db.Column(db.Float, default=0.0)
    confidence = db.Column(db.Float, default=0.0)
    presentation_skills = db.Column(db.Float, default=0.0)
    teamwork = db.Column(db.Float, default=0.0)
    leadership = db.Column(db.Float, default=0.0)
    problem_solving = db.Column(db.Float, default=0.0)
    # Added: finer-grained English-communication sub-dimensions
    grammar = db.Column(db.Float, default=0.0)
    vocabulary = db.Column(db.Float, default=0.0)
    pronunciation = db.Column(db.Float, default=0.0)
    fluency = db.Column(db.Float, default=0.0)

    # Computed outputs (0-100), persisted so Dashboard/Reports don't need
    # to recompute from scratch on every read
    communication_score = db.Column(db.Float, default=0.0)
    interview_readiness_contribution = db.Column(db.Float, default=0.0)
    strengths = db.Column(db.Text, nullable=True)     # JSON-encoded list
    weaknesses = db.Column(db.Text, nullable=True)    # JSON-encoded list
    suggestions = db.Column(db.Text, nullable=True)   # JSON-encoded list
    roadmap = db.Column(db.Text, nullable=True)        # JSON-encoded list of {week, focus, tasks}

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="communication_assessments")

    def __repr__(self):
        return f"<CommunicationAssessment student={self.student_id} score={self.communication_score}>"
