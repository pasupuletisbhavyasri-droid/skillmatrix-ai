from flask import Blueprint

placement_hub_bp = Blueprint("placement_hub", __name__, template_folder="../../templates/placement_hub")

from app.blueprints.placement_hub import routes  # noqa: E402,F401
