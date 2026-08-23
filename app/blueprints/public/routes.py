"""
Public-facing marketing pages:
Home, About, Features, Contact.
"""

from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
)

from app.blueprints.public import public_bp
from app.models import CareerRole, ContactMessage
from app.extensions import db


@public_bp.route("/")
def home():

    trending_careers = (
        CareerRole.query
        .filter_by(is_active=True)
        .order_by(CareerRole.view_count.desc())
        .limit(6)
        .all()
    )

    total_careers = (
        CareerRole.query
        .filter_by(is_active=True)
        .count()
    )

    return render_template(
        "public/home.html",
        trending_careers=trending_careers,
        total_careers=total_careers,
    )


@public_bp.route("/about")
def about():

    return render_template(
        "public/about.html"
    )


@public_bp.route("/features")
def features():

    return render_template(
        "public/features.html"
    )


@public_bp.route(
    "/contact",
    methods=["GET", "POST"]
)
def contact():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        # Validate name
        if not name:

            flash(
                "Please enter your name.",
                "danger"
            )

            return redirect(
                url_for("public.contact")
            )

        # Validate email
        if not email:

            flash(
                "Please enter your email.",
                "danger"
            )

            return redirect(
                url_for("public.contact")
            )

        # Validate message
        if not message:

            flash(
                "Please enter your message.",
                "danger"
            )

            return redirect(
                url_for("public.contact")
            )

        # Create contact message
        contact_message = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        # Save to database
        db.session.add(contact_message)
        db.session.commit()

        flash(
            "Thanks for reaching out! "
            "We'll get back to you soon.",
            "success"
        )

        return redirect(
            url_for("public.contact")
        )

    return render_template(
        "public/contact.html"
    )