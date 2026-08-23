"""
Aggregates all models so `from app.models import Student, CareerRole, ...`
works, and so Flask-Migrate can discover every table via a single import.
"""

from app.models.student import Student, Admin
from app.models.skill import Skill, StudentSkill, IndustrySkill, CareerSkill
from app.models.portfolio import Certification, Project, Resume
from app.models.career import CareerRole, Roadmap, Recommendation
from app.models.interview import InterviewQuestion, InterviewResult
from app.models.learning import Course, ProjectIdea, LearningResource
from app.models.library import Bookmark, FavoriteCareer, CareerGuide
from app.models.quiz import Quiz, QuizResult
from app.models.report import Report
from app.models.contact import ContactMessage
from app.models.system import Notification, ActivityLog
from app.models.communication import CommunicationAssessment
from app.models.placement import CampusDrive, DriveApplication


__all__ = [
    "Student", "Admin",

    "Skill", "StudentSkill", "IndustrySkill", "CareerSkill",

    "Certification", "Project", "Resume",

    "CareerRole", "Roadmap", "Recommendation",

    "InterviewQuestion", "InterviewResult",

    "Course", "ProjectIdea", "LearningResource",

    "Bookmark", "FavoriteCareer", "CareerGuide",

    "Quiz", "QuizResult",

    "Report",
    "ContactMessage",

    "Notification", "ActivityLog",

    "CommunicationAssessment",

    "CampusDrive", "DriveApplication",
]

