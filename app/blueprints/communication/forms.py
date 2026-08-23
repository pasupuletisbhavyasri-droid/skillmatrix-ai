"""WTForms for the Communication Analysis module."""
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class CommunicationAssessmentForm(FlaskForm):
    speaking_skills = FloatField("Speaking Skills (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    english_communication = FloatField("English Communication (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    grammar = FloatField("Grammar (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    vocabulary = FloatField("Vocabulary (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    pronunciation = FloatField("Pronunciation (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    fluency = FloatField("Fluency (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    confidence = FloatField("Confidence (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    presentation_skills = FloatField("Presentation Skills (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    teamwork = FloatField("Teamwork (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    leadership = FloatField("Leadership (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    problem_solving = FloatField("Problem Solving (0-10)", validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Analyze My Communication Skills")
