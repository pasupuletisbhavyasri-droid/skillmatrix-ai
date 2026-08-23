from flask import Blueprint

skill_gap_bp = Blueprint("skill_gap", __name__, template_folder="../../templates/skill_gap")

from app.blueprints.skill_gap import routes  # noqa: E402,F401
