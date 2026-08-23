from flask import Blueprint

recommendation_bp = Blueprint("recommendation", __name__, template_folder="../../templates/recommendation")

from app.blueprints.recommendation import routes  # noqa: E402,F401
