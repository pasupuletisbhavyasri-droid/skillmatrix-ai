from flask import Blueprint

resume_center_bp = Blueprint("resume_center", __name__, template_folder="../../templates/resume_center")

from app.blueprints.resume_center import routes  # noqa: E402,F401
