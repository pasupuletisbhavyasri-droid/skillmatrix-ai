"""CareerRole, Roadmap, Recommendation."""
from datetime import datetime
from app.extensions import db


class CareerRole(db.Model):
    __tablename__ = "career_roles"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    # Broad sector classification so Career Explorer / Recommendations can
    # filter across IT, Government, Private, Core Engineering, Non-IT —
    # separate from `category` (which is the finer-grained field, e.g.
    # "Artificial Intelligence") since a sector spans several categories.
    sector = db.Column(db.String(50), nullable=False, default="IT", index=True)

    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=True)

    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    growth_outlook = db.Column(db.String(255), nullable=True)
    future_scope = db.Column(db.Text, nullable=True)
    industry_demand_score = db.Column(db.Float, default=0.0)
    career_growth = db.Column(db.Text, nullable=True)

    resume_tips = db.Column(db.Text, nullable=True)
    portfolio_checklist = db.Column(db.Text, nullable=True)
    placement_tips = db.Column(db.Text, nullable=True)
    # JSON-encoded lists — kept as Text (like portfolio_checklist) rather
    # than new tables, since these are simple flat lists with no relational
    # behavior of their own (no FK targets, no per-item metadata needed).
    required_certifications = db.Column(db.Text, nullable=True)
    required_exams = db.Column(db.Text, nullable=True)
    companies_hiring = db.Column(db.Text, nullable=True)
    preferred_skills = db.Column(db.Text, nullable=True)   # JSON list of skill names, "nice to have"
    min_cgpa = db.Column(db.Float, nullable=True)           # typical placement/eligibility CGPA cutoff
    learning_resources = db.Column(db.Text, nullable=True)  # JSON list of {title, type, url}

    view_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    required_skills = db.relationship("CareerSkill", back_populates="career_role", cascade="all, delete-orphan")
    roadmap_steps = db.relationship("Roadmap", back_populates="career_role", cascade="all, delete-orphan",
                                     order_by="Roadmap.step_order")
    interview_questions = db.relationship("InterviewQuestion", back_populates="career_role", cascade="all, delete-orphan")
    project_ideas = db.relationship("ProjectIdea", back_populates="career_role", cascade="all, delete-orphan")
    recommendations = db.relationship("Recommendation", back_populates="career_role", cascade="all, delete-orphan")
    bookmarks = db.relationship("Bookmark", back_populates="career_role", cascade="all, delete-orphan")
    favorites = db.relationship("FavoriteCareer", back_populates="career_role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CareerRole {self.title}>"


class Roadmap(db.Model):
    __tablename__ = "roadmaps"

    id = db.Column(db.Integer, primary_key=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_link = db.Column(db.String(255), nullable=True)
    estimated_duration = db.Column(db.String(50), nullable=True)

    career_role = db.relationship("CareerRole", back_populates="roadmap_steps")


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey("career_roles.id"), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", back_populates="recommendations")
    career_role = db.relationship("CareerRole", back_populates="recommendations")
