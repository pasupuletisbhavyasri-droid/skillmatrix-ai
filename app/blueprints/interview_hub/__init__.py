from flask import Blueprint

interview_hub_bp = Blueprint("interview_hub", __name__, template_folder="../../templates/interview_hub")

from app.blueprints.interview_hub import routes  # noqa: E402,F401
