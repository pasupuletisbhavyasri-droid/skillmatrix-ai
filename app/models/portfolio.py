"""Certification, Project, Resume — student portfolio artifacts."""
from datetime import datetime
from app.extensions import db


class Certification(db.Model):
    __tablename__ = "certifications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(150), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    certificate_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="certifications")


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tech_stack = db.Column(db.String(255), nullable=True)
    github_link = db.Column(db.String(255), nullable=True)
    live_link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="projects")


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    ats_score = db.Column(db.Float, default=0.0)
    missing_keywords = db.Column(db.Text, nullable=True)
    parsed_text = db.Column(db.Text, nullable=True)
    # Full ATS analysis (strong/weak sections, explanation, suggestions)
    # as JSON, so the result page can show the complete breakdown without
    # needing to re-run analysis or re-parse the original file.
    analysis_json = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="resumes")
