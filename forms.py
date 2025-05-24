from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms import DateTimeLocalField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from datetime import datetime

from models import User, EventCategory

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Login As', choices=[
        ('admin', 'Administrator'), 
        ('organizer', 'Club Organizer'), 
        ('student', 'Regular Student')
    ], validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already registered. Please use a different one.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ClubForm(FlaskForm):
    name = StringField('Club Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    logo = FileField('Club Logo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Save Club')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    start_time = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=120)])
    category = SelectField('Category', choices=[(cat, cat) for cat in EventCategory.choices()], validators=[DataRequired()])
    max_participants = IntegerField('Maximum Participants', validators=[Optional()])
    poster = FileField('Event Poster', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    club_id = SelectField('Organizing Club', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Event')
    
    def validate_end_time(self, end_time):
        if end_time.data <= self.start_time.data:
            raise ValidationError('End time must be after start time.')
        
    def validate_start_time(self, start_time):
        if start_time.data < datetime.now():
            raise ValidationError('Start time cannot be in the past.')

class EventSearchForm(FlaskForm):
    query = StringField('Search Events', validators=[Optional()])
    category = SelectField('Category', choices=[('', 'All Categories')] + [(cat, cat) for cat in EventCategory.choices()], validators=[Optional()])
    date_from = DateTimeLocalField('From Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    date_to = DateTimeLocalField('To Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Search')

class CheckInForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    event_id = HiddenField('Event ID', validators=[DataRequired()])
    submit = SubmitField('Check In')

class RatingForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], 
                        coerce=int, validators=[DataRequired()])
    feedback = TextAreaField('Feedback', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Rating')
