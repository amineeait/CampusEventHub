from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

# Define user roles
class UserRole:
    ADMIN = 'admin'
    ORGANIZER = 'organizer'
    STUDENT = 'student'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.STUDENT)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    clubs = db.relationship('Club', backref='admin', lazy=True)
    organized_events = db.relationship('Event', backref='organizer', lazy=True)
    registrations = db.relationship('Registration', backref='user', lazy=True)
    attendances = db.relationship('Attendance', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    reminders = db.relationship('Reminder', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_organizer(self):
        return self.role == UserRole.ORGANIZER
    
    def is_student(self):
        return self.role == UserRole.STUDENT

class Club(db.Model):
    __tablename__ = 'clubs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo = db.Column(db.String(255), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    events = db.relationship('Event', backref='club', lazy=True)

class EventCategory:
    ACADEMIC = 'Academic'
    SOCIAL = 'Social'
    CULTURAL = 'Cultural'
    SPORTS = 'Sports'
    WORKSHOP = 'Workshop'
    SEMINAR = 'Seminar'
    OTHER = 'Other'
    
    @classmethod
    def choices(cls):
        return [cls.ACADEMIC, cls.SOCIAL, cls.CULTURAL, cls.SPORTS, cls.WORKSHOP, cls.SEMINAR, cls.OTHER]

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    max_participants = db.Column(db.Integer, nullable=True)
    poster = db.Column(db.String(255), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade="all, delete-orphan")
    attendances = db.relationship('Attendance', backref='event', lazy=True, cascade="all, delete-orphan")
    ratings = db.relationship('Rating', backref='event', lazy=True, cascade="all, delete-orphan")
    photos = db.relationship('Photo', backref='event', lazy=True, cascade="all, delete-orphan")
    reminders = db.relationship('Reminder', backref='event', lazy=True, cascade="all, delete-orphan")
    
    def is_past(self):
        return datetime.now() > self.end_time
    
    def is_upcoming(self):
        return datetime.now() < self.start_time
    
    def is_ongoing(self):
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    
    def get_registration_count(self):
        return Registration.query.filter_by(event_id=self.id).count()
    
    def get_attendance_count(self):
        return Attendance.query.filter_by(event_id=self.id).count()
    
    def get_average_rating(self):
        ratings = Rating.query.filter_by(event_id=self.id).all()
        if not ratings:
            return 0
        return sum(rating.rating for rating in ratings) / len(ratings)

class Registration(db.Model):
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_registration'),
    )

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_attendance'),
    )

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_rating'),
    )

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    photo_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    remind_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_reminder'),
    )
