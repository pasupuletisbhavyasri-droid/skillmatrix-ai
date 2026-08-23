"""
Skill taxonomy + junction tables.
"""
from datetime import datetime
from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(80), nullable=True)

    student_links = db.relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    career_links = db.relationship("CareerSkill", back_populates="skill", cascade="all, delete-orphan")
    industry_links = db.relationship("IndustrySkill", back_populates="skill", cascade="all, delete-orphan")
    courses = db.relationship("Course", back_populates="skill")

    def __repr__(self):
        return f"<Skill {self.name}>"


class StudentSkill(db.Model):
    __tablename__ = "student_skills"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    proficiency_level = db.Column(db.String(20), default="Beginner")
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="skills")
    skill = db.relationship("Skill", back_populates="student_links")

    __table_args__ = (db.UniqueConstraint("student_id", "skill_id", name="uq_student_skill"),)


class IndustrySkill(db.Model):
    __tablename__ = "industry_skills"

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    industry_category = db.Column(db.String(100), nullable=False)
    demand_score = db.Column(db.Float, default=0.0)

    skill = db.relationship("Skill", back_populates="industry_links")


class CareerSkill(db.Model):
    __tablename__ = "career_skills"

    id = db.Column(db.Integer, primary_key=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    required_level = db.Column(db.String(20), default="Intermediate")
    priority = db.Column(db.String(10), default="Medium")
    weight = db.Column(db.Float, default=1.0)

    career_role = db.relationship("CareerRole", back_populates="required_skills")
    skill = db.relationship("Skill", back_populates="career_links")

    __table_args__ = (db.UniqueConstraint("career_role_id", "skill_id", name="uq_career_skill"),)
