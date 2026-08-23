"""
Student and Admin models.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class Student(UserMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    photo_url = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.Date, nullable=True)

    college = db.Column(db.String(150), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    year = db.Column(db.String(20), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)

    address = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)

    career_interest = db.Column(db.String(150), nullable=True)
    communication_skill_rating = db.Column(db.Float, default=0.0)

    resume_score = db.Column(db.Float, default=0.0)
    employability_score = db.Column(db.Float, default=0.0)
    placement_readiness_score = db.Column(db.Float, default=0.0)

    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    skills = db.relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    certifications = db.relationship("Certification", back_populates="student", cascade="all, delete-orphan")
    projects = db.relationship("Project", back_populates="student", cascade="all, delete-orphan")
    resumes = db.relationship("Resume", back_populates="student", cascade="all, delete-orphan")
    recommendations = db.relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")
    interview_results = db.relationship("InterviewResult", back_populates="student", cascade="all, delete-orphan")
    bookmarks = db.relationship("Bookmark", back_populates="student", cascade="all, delete-orphan")
    favorites = db.relationship("FavoriteCareer", back_populates="student", cascade="all, delete-orphan")
    quiz_results = db.relationship("QuizResult", back_populates="student", cascade="all, delete-orphan")
    reports = db.relationship("Report", back_populates="student", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="student", cascade="all, delete-orphan")
    activity_logs = db.relationship("ActivityLog", back_populates="student", cascade="all, delete-orphan")
    communication_assessments = db.relationship("CommunicationAssessment", back_populates="student", cascade="all, delete-orphan")
    drive_applications = db.relationship("DriveApplication", back_populates="student", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<Student {self.student_code} {self.email}>"


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default="admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def get_id(self):
        return f"admin-{self.id}"

    def __repr__(self):
        return f"<Admin {self.email}>"
