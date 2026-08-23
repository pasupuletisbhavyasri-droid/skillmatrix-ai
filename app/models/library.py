"""Bookmark and FavoriteCareer."""
from datetime import datetime
from app.extensions import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="bookmarks")
    career_role = db.relationship("CareerRole", back_populates="bookmarks")

    __table_args__ = (db.UniqueConstraint("student_id", "career_role_id", name="uq_bookmark"),)


class FavoriteCareer(db.Model):
    __tablename__ = "favorite_careers"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="favorites")
    career_role = db.relationship("CareerRole", back_populates="favorites")

    __table_args__ = (db.UniqueConstraint("student_id", "career_role_id", name="uq_favorite"),)


class CareerGuide(db.Model):
    """
    Career Library — admin-authored articles/guides/roadmap write-ups,
    shown alongside bookmarks/favorites/trending. Kept as a simple flat
    model; no CMS-grade structure needed at this scale.
    """
    __tablename__ = "career_guides"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    guide_type = db.Column(db.String(30), default="Article")  # Article/Guide/Book/Roadmap
    category = db.Column(db.String(100), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    external_url = db.Column(db.String(255), nullable=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    career_role = db.relationship("CareerRole")

    def __repr__(self):
        return f"<CareerGuide {self.title}>"
