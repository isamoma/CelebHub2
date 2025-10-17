from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL

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
    is_featured = BooleanField('Featured')
    submit = SubmitField('Save')
