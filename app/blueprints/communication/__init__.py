from flask import Blueprint

communication_bp = Blueprint("communication", __name__, template_folder="../../templates/communication")

from app.blueprints.communication import routes  # noqa: E402,F401
