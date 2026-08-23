from flask import Blueprint

career_explorer_bp = Blueprint("career_explorer", __name__, template_folder="../../templates/career_explorer")

from app.blueprints.career_explorer import routes  # noqa: E402,F401
