"""
Resume Center: upload, ATS analysis, and history of past resume uploads,
plus the Resume Builder (generates a formatted resume PDF directly from
profile data, distinct from analyzing an uploaded file).
"""
import os
import json
from flask import render_template, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user

from app.blueprints.resume_center import resume_center_bp
from app.utils.decorators import student_required
from app.utils.validators import validate_file_upload
from app.extensions import db
from app.models import Resume, CareerRole, ActivityLog, Report
from app.blueprints.resume_center.forms import ResumeUploadForm
from app.services.resume_service import extract_text_from_file, analyze_resume
from app.services.employability_service import recalculate_and_save
from app.services import report_service


@resume_center_bp.route("/", methods=["GET", "POST"])
@login_required
@student_required
def index():
    form = ResumeUploadForm()
    form.target_role_id.choices = [(0, "General (no specific target)")] + [
        (r.id, r.title) for r in CareerRole.query.filter_by(is_active=True).order_by(CareerRole.title).all()
    ]

    if form.validate_on_submit():
        saved_relative_path = validate_file_upload(
            form.resume_file.data, subfolder="resumes",
            allowed_extensions=current_app.config["ALLOWED_RESUME_EXTENSIONS"],
        )
        if not saved_relative_path:
            flash("Resume upload failed validation. Please check the file type and size.", "danger")
            return redirect(url_for("resume_center.index"))

        full_path = os.path.normpath(os.path.join(current_app.static_folder, saved_relative_path))

        resume_text = extract_text_from_file(full_path)
        if not resume_text.strip():
            flash("Couldn't read text from this file — try re-saving it as a standard PDF/DOCX.", "warning")
            return redirect(url_for("resume_center.index"))

        target_role = None
        if form.target_role_id.data and form.target_role_id.data != 0:
            target_role = CareerRole.query.get(form.target_role_id.data)

        analysis = analyze_resume(resume_text, target_role=target_role)

        Resume.query.filter_by(student_id=current_user.id, is_active=True).update({"is_active": False})

        resume = Resume(
            student_id=current_user.id,
            filename=form.resume_file.data.filename,
            filepath=saved_relative_path,
            ats_score=analysis["ats_score"],
            missing_keywords=json.dumps(analysis["missing_keywords"]),
            parsed_text=resume_text[:5000],
            analysis_json=json.dumps({
                "strong_sections": analysis["strong_sections"],
                "weak_sections": analysis["weak_sections"],
                "suggestions": analysis["suggestions"],
                "explanation": analysis["explanation"],
                "matched_keywords": analysis["matched_keywords"],
            }),
            is_active=True,
        )
        db.session.add(resume)
        db.session.add(ActivityLog(student_id=current_user.id, action="Uploaded and analyzed resume"))
        db.session.commit()

        recalculate_and_save(current_user)

        flash("Resume analyzed successfully!", "success")
        return redirect(url_for("resume_center.result", resume_id=resume.id))

    resumes = Resume.query.filter_by(student_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return render_template("resume_center/index.html", form=form, resumes=resumes)


@resume_center_bp.route("/<int:resume_id>")
@login_required
@student_required
def result(resume_id):
    resume = Resume.query.filter_by(id=resume_id, student_id=current_user.id).first_or_404()
    missing_keywords = json.loads(resume.missing_keywords) if resume.missing_keywords else []
    analysis = json.loads(resume.analysis_json) if resume.analysis_json else {}
    return render_template(
        "resume_center/result.html", resume=resume, missing_keywords=missing_keywords,
        strong_sections=analysis.get("strong_sections", []),
        weak_sections=analysis.get("weak_sections", []),
        suggestions=analysis.get("suggestions", []),
        explanation=analysis.get("explanation", ""),
        matched_keywords=analysis.get("matched_keywords", []),
    )


@resume_center_bp.route("/builder")
@login_required
@student_required
def builder():
    templates = report_service.get_resume_templates()
    has_skills = bool(current_user.skills)
    return render_template("resume_center/builder.html", templates=templates, has_skills=has_skills)


@resume_center_bp.route("/builder/generate/<template_key>", methods=["POST"])
@login_required
@student_required
def builder_generate(template_key):
    report = report_service.build_resume_pdf(current_user, template_key=template_key)
    db.session.add(ActivityLog(student_id=current_user.id, action=f"Built resume ({template_key} template)"))
    db.session.commit()
    flash("Your resume has been generated!", "success")
    return redirect(url_for("resume_center.builder_result", report_id=report.id))


@resume_center_bp.route("/builder/result/<int:report_id>")
@login_required
@student_required
def builder_result(report_id):
    report = Report.query.filter_by(id=report_id, student_id=current_user.id, report_type="ResumeBuilder").first_or_404()
    return render_template("resume_center/builder_result.html", report=report)
