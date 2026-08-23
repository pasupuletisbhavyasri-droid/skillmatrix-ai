"""
Placement Hub:
- Placement readiness tracker
- Campus drives
- Student applications
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.placement_hub import placement_hub_bp
from app.utils.decorators import student_required
from app.extensions import db
from app.models import CampusDrive, DriveApplication
from app.services.placement_service import get_placement_readiness


# =========================================================
# PLACEMENT HUB HOME
# =========================================================

@placement_hub_bp.route("/")
@login_required
@student_required
def index():

    readiness = get_placement_readiness(current_user)

    return render_template(
        "placement_hub/index.html",
        readiness=readiness
    )


# =========================================================
# CAMPUS DRIVES
# =========================================================

@placement_hub_bp.route("/drives")
@login_required
@student_required
def drives():

    active_drives = (
        CampusDrive.query
        .filter_by(is_active=True)
        .order_by(CampusDrive.drive_date.asc())
        .all()
    )

    my_applications = {
        application.drive_id: application
        for application in (
            DriveApplication.query
            .filter_by(student_id=current_user.id)
            .all()
        )
    }

    return render_template(
        "placement_hub/drives.html",
        drives=active_drives,
        my_applications=my_applications
    )


# =========================================================
# APPLY TO CAMPUS DRIVE
# =========================================================

@placement_hub_bp.route(
    "/drives/<int:drive_id>/apply",
    methods=["POST"]
)
@login_required
@student_required
def apply_drive(drive_id):

    # Find the selected campus drive
    drive = CampusDrive.query.get_or_404(drive_id)

    # Check whether student already applied
    existing = (
        DriveApplication.query
        .filter_by(
            student_id=current_user.id,
            drive_id=drive.id
        )
        .first()
    )

    if existing:

        flash(
            "You have already applied to this campus drive.",
            "warning"
        )

        return redirect(
            url_for("placement_hub.drives")
        )

    # Create application
    application = DriveApplication(
        student_id=current_user.id,
        drive_id=drive.id,
        status="Applied"
    )

    db.session.add(application)
    db.session.commit()

    flash(
        f"Successfully applied to "
        f"{drive.company_name} — {drive.role_title}!",
        "success"
    )

    return redirect(
        url_for("placement_hub.drives")
    )


# =========================================================
# MY APPLICATIONS
# =========================================================

@placement_hub_bp.route("/applications")
@login_required
@student_required
def applications():

    my_applications = (
        DriveApplication.query
        .filter_by(student_id=current_user.id)
        .order_by(
            DriveApplication.applied_at.desc()
        )
        .all()
    )

    return render_template(
        "placement_hub/applications.html",
        applications=my_applications
    )