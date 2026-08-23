"""Course, ProjectIdea, LearningResource."""
from app.extensions import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    provider = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)
    level = db.Column(db.String(20), default="Beginner")

    skill = db.relationship("Skill", back_populates="courses")


class ProjectIdea(db.Model):
    __tablename__ = "project_ideas"

    id = db.Column(db.Integer, primary_key=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default="Beginner")

    career_role = db.relationship("CareerRole", back_populates="project_ideas")


class LearningResource(db.Model):
    __tablename__ = "learning_resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    resource_type = db.Column(db.String(30), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=True)
