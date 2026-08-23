"""
Configuration classes for different environments.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, ".env"))


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-.env-never-use-this-default-in-production")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
    ALLOWED_CERT_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

    CAREERS_PER_PAGE = 12
    STUDENTS_PER_PAGE_ADMIN = 20

    EMPLOYABILITY_WEIGHTS = {
        "cgpa": 20,
        "technical_skills": 30,
        "projects": 20,
        "certifications": 10,
        "resume": 10,
        "communication": 10,
    }


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'skillmatrix.db')}"
    )
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'skillmatrix.db')}"
    )
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        if app.config["SECRET_KEY"].startswith("change-me"):
            raise RuntimeError(
                "SECRET_KEY is not set. Set it via the SECRET_KEY environment "
                "variable before running in production."
            )


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
