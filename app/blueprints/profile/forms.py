"""WTForms for the Profile & Portfolio module."""

from datetime import date

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    FloatField,
    DateField,
    URLField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
    URL,
    ValidationError,
)


# ============================================================
# CUSTOM VALIDATORS
# ============================================================

def validate_person_name(form, field):
    """Validate the student's full name."""

    value = (field.data or "").strip()

    if not value:
        raise ValidationError("Full Name is required.")

    if not all(char.isalpha() or char in " .'-" for char in value):
        raise ValidationError(
            "Full Name can contain only letters, spaces, "
            "apostrophes, hyphens, and periods."
        )

    field.data = value


def validate_phone_number(form, field):
    """Validate an Indian 10-digit mobile number."""

    value = (field.data or "").strip()

    if not value:
        return

    if not value.isdigit():
        raise ValidationError(
            "Phone number must contain only digits."
        )

    if len(value) != 10:
        raise ValidationError(
            "Phone number must contain exactly 10 digits."
        )

    if value[0] not in "6789":
        raise ValidationError(
            "Enter a valid Indian mobile number."
        )

    field.data = value


def validate_date_of_birth(form, field):
    """Validate student's date of birth."""

    if not field.data:
        return

    today = date.today()

    if field.data > today:
        raise ValidationError(
            "Date of birth cannot be in the future."
        )

    age = today.year - field.data.year - (
        (today.month, today.day)
        < (field.data.month, field.data.day)
    )

    if age < 13:
        raise ValidationError(
            "Date of birth indicates an invalid age."
        )

    if age > 100:
        raise ValidationError(
            "Please enter a valid date of birth."
        )


def validate_college_name(form, field):
    """Validate college name."""

    value = (field.data or "").strip()

    if not value:
        raise ValidationError(
            "College name is required."
        )

    if len(value) < 2:
        raise ValidationError(
            "College name must contain at least 2 characters."
        )

    field.data = value


def validate_branch_name(form, field):
    """Validate academic branch name."""

    value = (field.data or "").strip()

    if not value:
        raise ValidationError(
            "Branch is required."
        )

    if len(value) < 2:
        raise ValidationError(
            "Branch must contain at least 2 characters."
        )

    field.data = value


def validate_address(form, field):
    """Validate and clean the student's address."""

    value = (field.data or "").strip()

    # Address is optional
    if not value:
        field.data = ""
        return

    if len(value) < 5:
        raise ValidationError(
            "Address must contain at least 5 characters."
        )

    field.data = value


def validate_github_url(form, field):
    """Validate GitHub profile URL."""

    value = (field.data or "").strip()

    if not value:
        return

    if not value.startswith(
        (
            "https://github.com/",
            "http://github.com/",
        )
    ):
        raise ValidationError(
            "Please enter a valid GitHub profile URL."
        )

    field.data = value


def validate_linkedin_url(form, field):
    """Validate LinkedIn profile URL."""

    value = (field.data or "").strip()

    if not value:
        return

    if not value.startswith(
        (
            "https://linkedin.com/",
            "http://linkedin.com/",
            "https://www.linkedin.com/",
            "http://www.linkedin.com/",
        )
    ):
        raise ValidationError(
            "Please enter a valid LinkedIn profile URL."
        )

    field.data = value


# ============================================================
# PROFILE EDIT FORM
# ============================================================

class ProfileEditForm(FlaskForm):
    """Form used to edit the student's profile."""

    # --------------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------------

    name = StringField(
        "Full Name",
        validators=[
            DataRequired(
                message="Full Name is required."
            ),
            Length(
                min=2,
                max=100
            ),
            validate_person_name,
        ],
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            validate_phone_number,
        ],
    )

    gender = SelectField(
        "Gender",
        choices=[
            ("", "Prefer not to say"),
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
        validators=[
            Optional()
        ],
    )

    dob = DateField(
        "Date of Birth",
        validators=[
            Optional(),
            validate_date_of_birth,
        ],
    )

    # --------------------------------------------------------
    # ACADEMIC INFORMATION
    # --------------------------------------------------------

    college = StringField(
        "College",
        validators=[
            DataRequired(
                message="College name is required."
            ),
            Length(
                min=2,
                max=150
            ),
            validate_college_name,
        ],
    )

    branch = StringField(
        "Branch",
        validators=[
            DataRequired(
                message="Branch is required."
            ),
            Length(
                min=2,
                max=100
            ),
            validate_branch_name,
        ],
    )

    year = SelectField(
        "Year",
        choices=[
            ("1st Year", "1st Year"),
            ("2nd Year", "2nd Year"),
            ("3rd Year", "3rd Year"),
        ],
        validators=[
            DataRequired(
                message="Please select your year."
            )
        ],
    )

    cgpa = FloatField(
        "CGPA",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=10,
                message="CGPA must be between 0 and 10.",
            ),
        ],
    )

    # --------------------------------------------------------
    # CONTACT / SOCIAL INFORMATION
    # --------------------------------------------------------

    address = StringField(
        "Address",
        validators=[
            Optional(),
            Length(
                max=255
            ),
            validate_address,
        ],
    )

    github_url = URLField(
        "GitHub URL",
        validators=[
            Optional(),
            URL(
                message="Enter a valid URL."
            ),
            validate_github_url,
        ],
    )

    linkedin_url = URLField(
        "LinkedIn URL",
        validators=[
            Optional(),
            URL(
                message="Enter a valid URL."
            ),
            validate_linkedin_url,
        ],
    )

    # --------------------------------------------------------
    # CAREER INFORMATION
    # --------------------------------------------------------

    career_interest = StringField(
        "Career Interest",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    communication_skill_rating = FloatField(
        "Self-Rated Communication (0-10)",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=10,
                message=(
                    "Communication rating must be between 0 and 10."
                ),
            ),
        ],
    )

    # --------------------------------------------------------
    # PROFILE PHOTO
    # --------------------------------------------------------

    photo = FileField(
        "Profile Photo",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png"],
                "Images only (jpg, jpeg, png).",
            ),
        ],
    )

    submit = SubmitField(
        "Save Changes"
    )


# ============================================================
# SKILL FORM
# ============================================================

class SkillForm(FlaskForm):
    """Form used to add a student skill."""

    skill_name = StringField(
        "Skill Name",
        validators=[
            DataRequired(),
            Length(
                max=100
            ),
        ],
    )

    proficiency_level = SelectField(
        "Proficiency",
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
            ("Expert", "Expert"),
        ],
        validators=[
            DataRequired()
        ],
    )

    submit = SubmitField(
        "Add Skill"
    )


# ============================================================
# PROJECT FORM
# ============================================================

class ProjectForm(FlaskForm):
    """Form used to add a student project."""

    title = StringField(
        "Project Title",
        validators=[
            DataRequired(),
            Length(
                max=150
            ),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(
                max=1000
            ),
        ],
    )

    tech_stack = StringField(
        "Tech Stack (comma-separated)",
        validators=[
            Optional(),
            Length(
                max=255
            ),
        ],
    )

    github_link = URLField(
        "GitHub Link",
        validators=[
            Optional(),
            URL()
        ],
    )

    live_link = URLField(
        "Live Demo Link",
        validators=[
            Optional(),
            URL()
        ],
    )

    submit = SubmitField(
        "Add Project"
    )


# ============================================================
# CERTIFICATION FORM
# ============================================================

class CertificationForm(FlaskForm):
    """Form used to add a certification."""

    title = StringField(
        "Certification Title",
        validators=[
            DataRequired(),
            Length(
                max=150
            ),
        ],
    )

    issuer = StringField(
        "Issuing Organization",
        validators=[
            Optional(),
            Length(
                max=150
            ),
        ],
    )

    issue_date = DateField(
        "Issue Date",
        validators=[
            Optional()
        ],
    )

    certificate_file = FileField(
        "Certificate File",
        validators=[
            Optional(),
            FileAllowed(
                ["pdf", "png", "jpg", "jpeg"],
                "PDF or image files only.",
            ),
        ],
    )

    submit = SubmitField(
        "Add Certification"
    )