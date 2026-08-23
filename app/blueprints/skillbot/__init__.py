from flask import Blueprint

skillbot_bp = Blueprint(
    "skillbot",
    __name__,
    url_prefix="/skillbot"
)

from app.blueprints.skillbot import routes