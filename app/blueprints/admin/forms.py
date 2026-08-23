"""WTForms for the Admin Panel."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SubmitField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class CareerRoleForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired(), Length(max=150)])
    slug = StringField("URL Slug", validators=[DataRequired(), Length(max=150)])
    category = StringField("Category", validators=[DataRequired(), Length(max=100)])
    sector = SelectField("Sector", choices=[
        ("IT", "IT"), ("Government", "Government"), ("Private", "Private"),
        ("Core Engineering", "Core Engineering"), ("Non-IT", "Non-IT"),
    ], validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    responsibilities = TextAreaField("Responsibilities", validators=[Optional()])
    salary_min = IntegerField("Minimum Salary", validators=[Optional(), NumberRange(min=0)])
    salary_max = IntegerField("Maximum Salary", validators=[Optional(), NumberRange(min=0)])
    growth_outlook = StringField("Growth Outlook", validators=[Optional(), Length(max=255)])
    future_scope = TextAreaField("Future Scope", validators=[Optional()])
    industry_demand_score = FloatField("Industry Demand Score (0-100)", validators=[Optional(), NumberRange(min=0, max=100)])
    career_growth = TextAreaField("Career Growth Path", validators=[Optional()])
    resume_tips = TextAreaField("Resume Tips", validators=[Optional()])
    placement_tips = TextAreaField("Placement Tips", validators=[Optional()])
    required_certifications_raw = TextAreaField("Required Certifications (one per line)", validators=[Optional()])
    required_exams_raw = TextAreaField("Required Exams (one per line, for Government roles)", validators=[Optional()])
    companies_hiring_raw = TextAreaField("Companies Hiring (one per line)", validators=[Optional()])
    is_active = BooleanField("Active (visible to students)", default=True)
    submit = SubmitField("Save Career Role")


class SkillManageForm(FlaskForm):
    name = StringField("Skill Name", validators=[DataRequired(), Length(max=100)])
    category = StringField("Category", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Save Skill")


class CampusDriveForm(FlaskForm):
    company_name = StringField("Company Name", validators=[DataRequired(), Length(max=150)])
    role_title = StringField("Role Title", validators=[DataRequired(), Length(max=150)])
    eligibility_criteria = TextAreaField("Eligibility Criteria", validators=[Optional()])
    min_cgpa = FloatField("Minimum CGPA", validators=[Optional(), NumberRange(min=0, max=10)])
    package_min = IntegerField("Package Min (annual)", validators=[Optional(), NumberRange(min=0)])
    package_max = IntegerField("Package Max (annual)", validators=[Optional(), NumberRange(min=0)])
    location = StringField("Location", validators=[Optional(), Length(max=150)])
    drive_date = DateField("Drive Date", validators=[Optional()])
    registration_deadline = DateField("Registration Deadline", validators=[Optional()])
    description = TextAreaField("Description", validators=[Optional()])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Campus Drive")


class CareerGuideForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    guide_type = SelectField("Type", choices=[
        ("Article", "Article"), ("Guide", "Guide"), ("Book", "Book"), ("Roadmap", "Roadmap"),
    ], validators=[DataRequired()])
    category = StringField("Category", validators=[Optional(), Length(max=100)])
    summary = TextAreaField("Summary", validators=[Optional()])
    content = TextAreaField("Content", validators=[Optional()])
    external_url = StringField("External URL (optional book/PDF link)", validators=[Optional(), Length(max=255)])
    is_active = BooleanField("Active (visible to students)", default=True)
    submit = SubmitField("Save Guide")
