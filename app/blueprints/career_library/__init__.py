from flask import Blueprint

career_library_bp = Blueprint("career_library", __name__, template_folder="../../templates/career_library")

from app.blueprints.career_library import routes  # noqa: E402,F401
