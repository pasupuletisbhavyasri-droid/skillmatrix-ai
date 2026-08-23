from flask import Blueprint

practice_hub_bp = Blueprint("practice_hub", __name__, template_folder="../../templates/practice_hub")

from app.blueprints.practice_hub import routes  # noqa: E402,F401
