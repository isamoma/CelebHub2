from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, FileField, SubmitField,EmailField
from wtforms.validators import DataRequired, Length, Optional, URL ,Email

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])

class CelebrityForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=140)])
    slug = StringField('Slug', validators=[DataRequired(), Length(max=160)])
    category = StringField('Category', validators=[Optional(), Length(max=80)])
    photo = FileField('Photo (optional)')
    bio = TextAreaField('Bio', validators=[Optional()])
    youtube = StringField('YouTube URL', validators=[Optional(), URL()])
    tiktok = StringField('TikTok URL', validators=[Optional(), URL()])
    spotify = StringField('Spotify URL', validators=[Optional(), URL()])
    featured =BooleanField('Feature this celebrity')
    submit = SubmitField('Save')

class DeleteCelebrityForm(FlaskForm):
    submit = SubmitField('Delete')
class FeaturedForm(FlaskForm):
    featured =BooleanField('Feature this celebrity')
    submit=SubmitField('Save')

class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Your Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send Message')

class CelebritySubmissionForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired()])
    category = StringField("Category (Musician, Actor, Influencer...)", validators=[DataRequired()])
    bio = TextAreaField("Short Bio", validators=[DataRequired()])
    youtube = StringField("YouTube Link")
    tiktok = StringField("TikTok Link")
    spotify = StringField("Spotify Link")
    photo = FileField("Profile Photo")
class OnboardingForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=9, max=20)])
    message = TextAreaField("Tell us why you want to join CelebHub", validators=[Length(max=500)])
    submit = SubmitField("Submit")
