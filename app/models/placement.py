"""
Placement Hub — Campus Drives.

CampusDrive: an admin-managed campus recruitment drive (company, role,
eligibility, package, location). DriveApplication: a student's application
status against a specific drive — kept as a separate table (not a column
on CampusDrive) since many students apply to one drive.
"""
from datetime import datetime
from app.extensions import db


class CampusDrive(db.Model):
    __tablename__ = "campus_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    role_title = db.Column(db.String(150), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=True)

    eligibility_criteria = db.Column(db.Text, nullable=True)   # free text, e.g. "CGPA >= 7.0, no active backlogs"
    min_cgpa = db.Column(db.Float, nullable=True)
    package_min = db.Column(db.Integer, nullable=True)          # annual CTC
    package_max = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(150), nullable=True)
    drive_date = db.Column(db.Date, nullable=True)
    registration_deadline = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    career_role = db.relationship("CareerRole")
    applications = db.relationship("DriveApplication", back_populates="drive", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CampusDrive {self.company_name} - {self.role_title}>"


class DriveApplication(db.Model):
    __tablename__ = "drive_applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("campus_drives.id"), nullable=False)
    status = db.Column(db.String(30), default="Applied")  # Applied/Shortlisted/Interview Scheduled/Selected/Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    student = db.relationship("Student", back_populates="drive_applications")
    drive = db.relationship("CampusDrive", back_populates="applications")

    __table_args__ = (db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),)
