"""
Admin Panel: dashboard analytics, student directory, career role CRUD,
industry skill management, reports overview, settings.
"""
import json
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.admin import admin_bp
from app.utils.decorators import admin_required
from app.extensions import db
from app.models import (
    Student, CareerRole, Skill, Report, ActivityLog, Recommendation, CampusDrive, DriveApplication, CareerGuide
)
from app.blueprints.admin.forms import CareerRoleForm, SkillManageForm, CampusDriveForm, CareerGuideForm


def _lines_to_json(raw_text: str) -> str:
    """Converts a newline-separated textarea into a JSON-encoded list,
    dropping blank lines — used for certifications/exams/companies fields."""
    if not raw_text:
        return json.dumps([])
    items = [line.strip() for line in raw_text.splitlines() if line.strip()]
    return json.dumps(items)


def _json_to_lines(raw_json: str) -> str:
    """Reverse of _lines_to_json — used to pre-fill the edit form textarea."""
    if not raw_json:
        return ""
    try:
        items = json.loads(raw_json)
        return "\n".join(items)
    except (ValueError, TypeError):
        return ""


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_students": Student.query.count(),
        "active_students": Student.query.filter_by(is_active_account=True).count(),
        "total_careers": CareerRole.query.count(),
        "total_skills": Skill.query.count(),
        "reports_generated": Report.query.count(),
        "recommendations_generated": Recommendation.query.count(),
    }

    avg_employability = db.session.query(db.func.avg(Student.employability_score)).scalar() or 0

    recent_signups = Student.query.order_by(Student.created_at.desc()).limit(8).all()

    top_categories = (
        db.session.query(CareerRole.category, db.func.count(CareerRole.id))
        .group_by(CareerRole.category)
        .order_by(db.func.count(CareerRole.id).desc())
        .limit(6)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        stats=stats, avg_employability=round(avg_employability, 1),
        recent_signups=recent_signups, top_categories=top_categories,
    )


@admin_bp.route("/students")
@login_required
@admin_required
def students():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()

    query = Student.query
    if search:
        query = query.filter(
            db.or_(Student.name.ilike(f"%{search}%"), Student.email.ilike(f"%{search}%"))
        )

    pagination = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/students.html", pagination=pagination, search=search)


@admin_bp.route("/students/<int:student_id>")
@login_required
@admin_required
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    activity = ActivityLog.query.filter_by(student_id=student.id).order_by(ActivityLog.timestamp.desc()).limit(15).all()
    return render_template("admin/student_detail.html", student=student, activity=activity)


@admin_bp.route("/students/<int:student_id>/toggle-active", methods=["POST"])
@login_required
@admin_required
def toggle_student_active(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_active_account = not student.is_active_account
    db.session.commit()
    flash(f"{student.name}'s account is now {'active' if student.is_active_account else 'deactivated'}.", "info")
    return redirect(url_for("admin.student_detail", student_id=student_id))


@admin_bp.route("/careers")
@login_required
@admin_required
def careers():
    all_roles = CareerRole.query.order_by(CareerRole.title).all()
    return render_template("admin/careers.html", roles=all_roles)


@admin_bp.route("/careers/new", methods=["GET", "POST"])
@login_required
@admin_required
def career_create():
    form = CareerRoleForm()
    if form.validate_on_submit():
        if CareerRole.query.filter_by(slug=form.slug.data).first():
            flash("A career role with this slug already exists.", "danger")
            return render_template("admin/career_form.html", form=form, mode="Create")

        role = CareerRole(
            title=form.title.data, slug=form.slug.data, category=form.category.data,
            sector=form.sector.data,
            description=form.description.data, responsibilities=form.responsibilities.data,
            salary_min=form.salary_min.data, salary_max=form.salary_max.data,
            growth_outlook=form.growth_outlook.data, future_scope=form.future_scope.data,
            industry_demand_score=form.industry_demand_score.data or 0,
            career_growth=form.career_growth.data,
            resume_tips=form.resume_tips.data, placement_tips=form.placement_tips.data,
            required_certifications=_lines_to_json(form.required_certifications_raw.data),
            required_exams=_lines_to_json(form.required_exams_raw.data),
            companies_hiring=_lines_to_json(form.companies_hiring_raw.data),
            is_active=form.is_active.data,
        )
        db.session.add(role)
        db.session.commit()
        flash(f"Career role '{role.title}' created.", "success")
        return redirect(url_for("admin.careers"))

    return render_template("admin/career_form.html", form=form, mode="Create")


@admin_bp.route("/careers/<int:role_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def career_edit(role_id):
    role = CareerRole.query.get_or_404(role_id)
    form = CareerRoleForm(obj=role)

    if request.method == "GET":
        form.required_certifications_raw.data = _json_to_lines(role.required_certifications)
        form.required_exams_raw.data = _json_to_lines(role.required_exams)
        form.companies_hiring_raw.data = _json_to_lines(role.companies_hiring)

    if form.validate_on_submit():
        form.populate_obj(role)
        role.required_certifications = _lines_to_json(form.required_certifications_raw.data)
        role.required_exams = _lines_to_json(form.required_exams_raw.data)
        role.companies_hiring = _lines_to_json(form.companies_hiring_raw.data)
        db.session.commit()
        flash(f"Career role '{role.title}' updated.", "success")
        return redirect(url_for("admin.careers"))

    return render_template("admin/career_form.html", form=form, mode="Edit", role=role)


@admin_bp.route("/careers/<int:role_id>/delete", methods=["POST"])
@login_required
@admin_required
def career_delete(role_id):
    role = CareerRole.query.get_or_404(role_id)
    role.is_active = False
    db.session.commit()
    flash(f"Career role '{role.title}' deactivated.", "info")
    return redirect(url_for("admin.careers"))


@admin_bp.route("/skills")
@login_required
@admin_required
def skills():
    all_skills = Skill.query.order_by(Skill.name).all()
    return render_template("admin/skills.html", skills=all_skills, form=SkillManageForm())


@admin_bp.route("/skills/add", methods=["POST"])
@login_required
@admin_required
def skill_add():
    form = SkillManageForm()
    if form.validate_on_submit():
        if Skill.query.filter(db.func.lower(Skill.name) == form.name.data.lower()).first():
            flash("This skill already exists.", "warning")
        else:
            db.session.add(Skill(name=form.name.data.strip(), category=form.category.data))
            db.session.commit()
            flash("Skill added.", "success")
    return redirect(url_for("admin.skills"))


@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics():
    employability_distribution = _bucket_scores(
        [s.employability_score for s in Student.query.with_entities(Student.employability_score).all()]
    )
    category_counts = (
        db.session.query(CareerRole.category, db.func.count(CareerRole.id))
        .group_by(CareerRole.category).all()
    )
    most_bookmarked = (
        db.session.query(CareerRole.title, db.func.count().label("cnt"))
        .join(CareerRole.bookmarks)
        .group_by(CareerRole.id)
        .order_by(db.desc("cnt"))
        .limit(10)
        .all()
    )
    return render_template(
        "admin/analytics.html",
        employability_distribution=employability_distribution,
        category_counts=category_counts,
        most_bookmarked=most_bookmarked,
    )


def _bucket_scores(scores) -> dict:
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for raw in scores:
        s = raw[0] if isinstance(raw, tuple) else raw
        s = s or 0
        if s <= 20: buckets["0-20"] += 1
        elif s <= 40: buckets["21-40"] += 1
        elif s <= 60: buckets["41-60"] += 1
        elif s <= 80: buckets["61-80"] += 1
        else: buckets["81-100"] += 1
    return buckets


@admin_bp.route("/settings")
@login_required
@admin_required
def settings():
    return render_template("admin/settings.html")


# ---------------- Campus Drives ----------------

@admin_bp.route("/drives")
@login_required
@admin_required
def drives():
    all_drives = CampusDrive.query.order_by(CampusDrive.created_at.desc()).all()
    return render_template("admin/drives.html", drives=all_drives)


@admin_bp.route("/drives/new", methods=["GET", "POST"])
@login_required
@admin_required
def drive_create():
    form = CampusDriveForm()
    if form.validate_on_submit():
        drive = CampusDrive(
            company_name=form.company_name.data, role_title=form.role_title.data,
            eligibility_criteria=form.eligibility_criteria.data, min_cgpa=form.min_cgpa.data,
            package_min=form.package_min.data, package_max=form.package_max.data,
            location=form.location.data, drive_date=form.drive_date.data,
            registration_deadline=form.registration_deadline.data, description=form.description.data,
            is_active=form.is_active.data,
        )
        db.session.add(drive)
        db.session.commit()
        flash(f"Campus drive for {drive.company_name} created.", "success")
        return redirect(url_for("admin.drives"))
    return render_template("admin/drive_form.html", form=form, mode="Create")


@admin_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def drive_edit(drive_id):
    drive = CampusDrive.query.get_or_404(drive_id)
    form = CampusDriveForm(obj=drive)
    if form.validate_on_submit():
        form.populate_obj(drive)
        db.session.commit()
        flash(f"Campus drive for {drive.company_name} updated.", "success")
        return redirect(url_for("admin.drives"))
    return render_template("admin/drive_form.html", form=form, mode="Edit", drive=drive)


@admin_bp.route("/drives/<int:drive_id>/applications")
@login_required
@admin_required
def drive_applications(drive_id):
    drive = CampusDrive.query.get_or_404(drive_id)
    apps = DriveApplication.query.filter_by(drive_id=drive.id).order_by(DriveApplication.applied_at.desc()).all()
    return render_template("admin/drive_applications.html", drive=drive, applications=apps)


@admin_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@login_required
@admin_required
def update_application_status(application_id):
    application = DriveApplication.query.get_or_404(application_id)
    new_status = request.form.get("status")
    if new_status in ("Applied", "Shortlisted", "Interview Scheduled", "Selected", "Rejected"):
        application.status = new_status
        db.session.commit()
        flash("Application status updated.", "success")
    return redirect(url_for("admin.drive_applications", drive_id=application.drive_id))


# ---------------- Career Guides (Career Library) ----------------

@admin_bp.route("/guides")
@login_required
@admin_required
def guides():
    all_guides = CareerGuide.query.order_by(CareerGuide.created_at.desc()).all()
    return render_template("admin/guides.html", guides=all_guides)


@admin_bp.route("/guides/new", methods=["GET", "POST"])
@login_required
@admin_required
def guide_create():
    form = CareerGuideForm()
    if form.validate_on_submit():
        guide = CareerGuide(
            title=form.title.data, guide_type=form.guide_type.data, category=form.category.data,
            summary=form.summary.data, content=form.content.data,
            external_url=form.external_url.data or None, is_active=form.is_active.data,
        )
        db.session.add(guide)
        db.session.commit()
        flash(f"Guide '{guide.title}' created.", "success")
        return redirect(url_for("admin.guides"))
    return render_template("admin/guide_form.html", form=form, mode="Create")


@admin_bp.route("/guides/<int:guide_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def guide_edit(guide_id):
    guide = CareerGuide.query.get_or_404(guide_id)
    form = CareerGuideForm(obj=guide)
    if form.validate_on_submit():
        form.populate_obj(guide)
        guide.external_url = form.external_url.data or None
        db.session.commit()
        flash(f"Guide '{guide.title}' updated.", "success")
        return redirect(url_for("admin.guides"))
    return render_template("admin/guide_form.html", form=form, mode="Edit", guide=guide)


@admin_bp.route("/guides/<int:guide_id>/delete", methods=["POST"])
@login_required
@admin_required
def guide_delete(guide_id):
    guide = CareerGuide.query.get_or_404(guide_id)
    guide.is_active = False
    db.session.commit()
    flash(f"Guide '{guide.title}' deactivated.", "info")
    return redirect(url_for("admin.guides"))
