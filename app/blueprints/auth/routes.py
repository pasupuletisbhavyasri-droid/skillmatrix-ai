"""
Auth blueprint: student registration/login/logout + admin login.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models import Student, Admin, ActivityLog
from app.blueprints.auth.forms import RegisterForm, LoginForm, AdminLoginForm
from app.utils.helpers import generate_student_code


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        student = Student(
            student_code=generate_student_code(),
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data,
            college=form.college.data.strip(),
            branch=form.branch.data.strip(),
            year=form.year.data,
        )
        student.set_password(form.password.data)

        db.session.add(student)
        db.session.commit()

        db.session.add(ActivityLog(student_id=student.id, action="Account created"))
        db.session.commit()

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(email=form.email.data.lower().strip()).first()

        if student is None or not student.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)

        if not student.is_active_account:
            flash("This account has been deactivated. Contact support.", "warning")
            return render_template("auth/login.html", form=form)

        login_user(student, remember=(form.remember_me.data == "1"))

        db.session.add(ActivityLog(student_id=student.id, action="Logged in"))
        db.session.commit()

        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        if isinstance(current_user, Admin):
            return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        admin = Admin.query.filter_by(email=email).first()

        if admin is None:
            flash("Admin account not found.", "danger")
            return render_template("auth/admin_login.html", form=form)

        if not admin.check_password(password):
            flash("Incorrect admin password.", "danger")
            return render_template("auth/admin_login.html", form=form)

        login_user(admin, remember=False)

        flash("Admin login successful!", "success")

        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        for field_name, errors in form.errors.items():
            for error in errors:
                flash(f"{field_name}: {error}", "danger")

    return render_template("auth/admin_login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    is_admin = isinstance(current_user, Admin)
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.admin_login") if is_admin else url_for("public.home"))
