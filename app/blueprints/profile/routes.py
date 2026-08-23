"""
Profile & Portfolio blueprint.
"""
from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from app.blueprints.profile import profile_bp
from app.utils.decorators import student_required
from app.utils.validators import validate_file_upload
from app.utils.helpers import cgpa_category
from app.extensions import db
from app.models import Skill, StudentSkill, Project, Certification, ActivityLog
from app.blueprints.profile.forms import (
    ProfileEditForm, SkillForm, ProjectForm, CertificationForm
)
from app.services.employability_service import recalculate_and_save


@profile_bp.route("/")
@login_required
@student_required
def index():
    student = current_user
    return render_template(
        "profile/index.html",
        student=student,
        skills=student.skills,
        projects=student.projects,
        certifications=student.certifications,
        skill_form=SkillForm(),
        project_form=ProjectForm(),
        certification_form=CertificationForm(),
        cgpa_info=cgpa_category(student.cgpa),
    )


@profile_bp.route("/edit", methods=["GET", "POST"])
@login_required
@student_required
def edit():
    student = current_user
    form = ProfileEditForm(obj=student)

    if form.validate_on_submit():
        student.name = form.name.data.strip()
        student.phone = form.phone.data
        student.gender = form.gender.data or None
        student.dob = form.dob.data
        student.college = form.college.data.strip()
        student.branch = form.branch.data.strip()
        student.year = form.year.data
        student.cgpa = form.cgpa.data
        student.address = form.address.data
        student.github_url = form.github_url.data
        student.linkedin_url = form.linkedin_url.data
        student.career_interest = form.career_interest.data
        student.communication_skill_rating = form.communication_skill_rating.data

        if form.photo.data:
            saved_path = validate_file_upload(
                form.photo.data, subfolder="photos",
                allowed_extensions=current_app.config["ALLOWED_IMAGE_EXTENSIONS"],
            )
            if saved_path:
                student.photo_url = saved_path
            else:
                flash("Photo upload failed validation and was skipped.", "warning")

        db.session.add(ActivityLog(student_id=student.id, action="Updated profile"))
        db.session.commit()
        recalculate_and_save(student)

        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.index"))

    return render_template("profile/edit.html", form=form)


@profile_bp.route("/skills/add", methods=["POST"])
@login_required
@student_required
def add_skill():
    form = SkillForm()
    if form.validate_on_submit():
        skill_name = form.skill_name.data.strip()

        skill = Skill.query.filter(db.func.lower(Skill.name) == skill_name.lower()).first()
        if not skill:
            skill = Skill(name=skill_name)
            db.session.add(skill)
            db.session.flush()

        existing_link = StudentSkill.query.filter_by(student_id=current_user.id, skill_id=skill.id).first()
        if existing_link:
            flash(f"You've already added '{skill.name}'.", "warning")
        else:
            db.session.add(StudentSkill(
                student_id=current_user.id, skill_id=skill.id,
                proficiency_level=form.proficiency_level.data,
            ))
            db.session.commit()
            recalculate_and_save(current_user)
            flash(f"Added skill: {skill.name}", "success")
    else:
        flash("Please provide a valid skill name.", "danger")

    return redirect(url_for("profile.index"))


@profile_bp.route("/skills/<int:skill_link_id>/delete", methods=["POST"])
@login_required
@student_required
def delete_skill(skill_link_id):
    link = StudentSkill.query.filter_by(id=skill_link_id, student_id=current_user.id).first_or_404()
    db.session.delete(link)
    db.session.commit()
    recalculate_and_save(current_user)
    flash("Skill removed.", "info")
    return redirect(url_for("profile.index"))


@profile_bp.route("/projects/add", methods=["POST"])
@login_required
@student_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            student_id=current_user.id,
            title=form.title.data.strip(),
            description=form.description.data,
            tech_stack=form.tech_stack.data,
            github_link=form.github_link.data,
            live_link=form.live_link.data,
        )
        db.session.add(project)
        db.session.add(ActivityLog(student_id=current_user.id, action=f"Added project: {project.title}"))
        db.session.commit()
        recalculate_and_save(current_user)
        flash("Project added.", "success")
    else:
        flash("Please check the project details and try again.", "danger")

    return redirect(url_for("profile.index"))


@profile_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
@student_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id, student_id=current_user.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    recalculate_and_save(current_user)
    flash("Project removed.", "info")
    return redirect(url_for("profile.index"))


@profile_bp.route("/certifications/add", methods=["POST"])
@login_required
@student_required
def add_certification():
    form = CertificationForm()
    if form.validate_on_submit():
        cert = Certification(
            student_id=current_user.id,
            title=form.title.data.strip(),
            issuer=form.issuer.data,
            issue_date=form.issue_date.data,
        )
        if form.certificate_file.data:
            saved_path = validate_file_upload(
                form.certificate_file.data, subfolder="certificates",
                allowed_extensions=current_app.config["ALLOWED_CERT_EXTENSIONS"],
            )
            if saved_path:
                cert.certificate_url = saved_path

        db.session.add(cert)
        db.session.add(ActivityLog(student_id=current_user.id, action=f"Added certification: {cert.title}"))
        db.session.commit()
        recalculate_and_save(current_user)
        flash("Certification added.", "success")
    else:
        flash("Please check the certification details and try again.", "danger")

    return redirect(url_for("profile.index"))


@profile_bp.route("/certifications/<int:cert_id>/delete", methods=["POST"])
@login_required
@student_required
def delete_certification(cert_id):
    cert = Certification.query.filter_by(id=cert_id, student_id=current_user.id).first_or_404()
    db.session.delete(cert)
    db.session.commit()
    recalculate_and_save(current_user)
    flash("Certification removed.", "info")
    return redirect(url_for("profile.index"))
