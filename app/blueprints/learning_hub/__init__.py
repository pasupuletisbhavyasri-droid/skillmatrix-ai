from flask import Blueprint

learning_hub_bp = Blueprint("learning_hub", __name__, template_folder="../../templates/learning_hub")

from app.blueprints.learning_hub import routes  # noqa: E402,F401
