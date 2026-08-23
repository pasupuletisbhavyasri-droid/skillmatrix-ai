from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, SubmitField


class ResumeUploadForm(FlaskForm):
    resume_file = FileField("Upload Resume", validators=[
        FileRequired(message="Please select a file."),
        FileAllowed(["pdf", "doc", "docx"], "PDF or Word documents only."),
    ])
    target_role_id = SelectField("Target Career (optional)", coerce=int, validators=[])
    submit = SubmitField("Analyze Resume")
