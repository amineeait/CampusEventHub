import os
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

from app import app, db
from forms import (RegistrationForm, LoginForm, UpdateProfileForm, ChangePasswordForm,
                  ClubForm, EventForm, EventSearchForm, CheckInForm, RatingForm)
from models import User, UserRole, Club, Event, Registration, Attendance, Rating, Photo, Reminder
from utils import (save_file, get_event_stats, get_user_events_stats, 
                  generate_qr_code, export_participant_list)

# Custom filters
@app.template_filter('format_datetime')
def format_datetime_filter(value, format='%Y-%m-%d %H:%M'):
    if value:
        return value.strftime(format)
    return ""

@app.template_filter('nl2br')
def nl2br_filter(value):
    """Convert newlines to HTML line breaks."""
    if value:
        return value.replace('\n', '<br>')
    return ""

# Basic routes
@app.route('/')
def index():
    upcoming_events = Event.query.filter(Event.start_time > datetime.now()).order_by(Event.start_time).limit(6).all()
    categories = sorted(set([event.category for event in Event.query.all()]))
    return render_template('index.html', upcoming_events=upcoming_events, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # Direct to appropriate dashboard based on user's role
            if user.is_admin():
                return redirect(next_page or url_for('admin_dashboard'))
            elif user.is_organizer():
                return redirect(next_page or url_for('organizer_dashboard'))
            else:
                return redirect(next_page or url_for('student_dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Get the selected role from the form
        selected_role = form.role.data
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=selected_role
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    elif current_user.is_organizer():
        return redirect(url_for('organizer_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

# Profile routes
@app.route('/profile')
@login_required
def profile():
    return render_template('profile/view.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_file(form.profile_picture.data, 'uploads/profile_pics')
            current_user.profile_picture = picture_file
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
    
    return render_template('profile/edit.html', form=form)

@app.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect!', 'danger')
            return render_template('profile/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile/edit.html', form=form, change_password=True)

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        abort(403)
    
    total_users = User.query.count()
    total_events = Event.query.count()
    total_clubs = Club.query.count()
    total_registrations = Registration.query.count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    
    user_roles = {
        'Admin': User.query.filter_by(role=UserRole.ADMIN).count(),
        'Organizer': User.query.filter_by(role=UserRole.ORGANIZER).count(),
        'Student': User.query.filter_by(role=UserRole.STUDENT).count()
    }
    
    return render_template('admin/dashboard.html', 
                           total_users=total_users,
                           total_events=total_events,
                           total_clubs=total_clubs,
                           total_registrations=total_registrations,
                           recent_users=recent_users,
                           recent_events=recent_events,
                           user_roles=user_roles)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin():
        abort(403)
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/change-role/<role>')
@login_required
def change_user_role(user_id, role):
    if not current_user.is_admin():
        abort(403)
    
    if role not in [UserRole.ADMIN, UserRole.ORGANIZER, UserRole.STUDENT]:
        flash('Invalid role', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent the last admin from demoting themselves
    if user.is_admin() and user.id == current_user.id:
        admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
        if admin_count <= 1 and role != UserRole.ADMIN:
            flash('Cannot change role. You are the only admin.', 'danger')
            return redirect(url_for('admin_users'))
    
    user.role = role
    db.session.commit()
    flash(f'User role updated to {role}', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/clubs')
@login_required
def admin_clubs():
    if not current_user.is_admin():
        abort(403)
    
    clubs = Club.query.all()
    return render_template('admin/clubs.html', clubs=clubs)

@app.route('/admin/club/new', methods=['GET', 'POST'])
@login_required
def create_club():
    if not current_user.is_admin():
        abort(403)
    
    form = ClubForm()
    
    if form.validate_on_submit():
        logo_file = None
        if form.logo.data:
            logo_file = save_file(form.logo.data, 'uploads/club_logos')
        
        club = Club(
            name=form.name.data,
            description=form.description.data,
            logo=logo_file,
            admin_id=current_user.id
        )
        
        db.session.add(club)
        db.session.commit()
        flash('Club created successfully!', 'success')
        return redirect(url_for('admin_clubs'))
    
    return render_template('admin/clubs.html', form=form, create_club=True)

@app.route('/admin/club/<int:club_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_club(club_id):
    if not current_user.is_admin():
        abort(403)
    
    club = Club.query.get_or_404(club_id)
    form = ClubForm()
    
    if form.validate_on_submit():
        if form.logo.data:
            logo_file = save_file(form.logo.data, 'uploads/club_logos')
            club.logo = logo_file
        
        club.name = form.name.data
        club.description = form.description.data
        
        db.session.commit()
        flash('Club updated successfully!', 'success')
        return redirect(url_for('admin_clubs'))
    
    elif request.method == 'GET':
        form.name.data = club.name
        form.description.data = club.description
    
    return render_template('admin/clubs.html', form=form, edit_club=True, club=club)

@app.route('/admin/club/<int:club_id>/delete', methods=['POST'])
@login_required
def delete_club(club_id):
    if not current_user.is_admin():
        abort(403)
    
    club = Club.query.get_or_404(club_id)
    
    # Check if club has events
    if club.events:
        flash('Cannot delete club with associated events', 'danger')
        return redirect(url_for('admin_clubs'))
    
    db.session.delete(club)
    db.session.commit()
    flash('Club deleted successfully!', 'success')
    return redirect(url_for('admin_clubs'))

# Organizer routes
@app.route('/organizer/create-club', methods=['GET', 'POST'])
@login_required
def organizer_create_club():
    # Check if user is an organizer or admin
    if not current_user.is_organizer() and not current_user.is_admin():
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ClubForm()
    if form.validate_on_submit():
        logo_file = None
        if form.logo.data:
            logo_file = save_file(form.logo.data, 'uploads/club_logos')
        
        club = Club(
            name=form.name.data,
            description=form.description.data,
            logo=logo_file,
            admin_id=current_user.id
        )
        
        db.session.add(club)
        db.session.commit()
        flash('Club created successfully! Now you can create events for this club.', 'success')
        return redirect(url_for('organizer_dashboard'))
    
    return render_template('organizer/create_club.html', form=form)

@app.route('/organizer/dashboard')
@login_required
def organizer_dashboard():
    if not (current_user.is_organizer() or current_user.is_admin()):
        abort(403)
    
    # Get clubs administered by the user
    clubs = Club.query.filter_by(admin_id=current_user.id).all()
    
    # Get all events organized by the user
    events = Event.query.filter_by(organizer_id=current_user.id).all()
    
    # Get event statistics
    event_stats = get_event_stats(events)
    
    # Get recent registrations for user's events
    event_ids = [event.id for event in events]
    recent_registrations = Registration.query.filter(Registration.event_id.in_(event_ids)).order_by(Registration.registration_time.desc()).limit(10).all()
    
    return render_template('organizer/dashboard.html',
                          clubs=clubs,
                          events=events,
                          event_stats=event_stats,
                          recent_registrations=recent_registrations)

@app.route('/organizer/events')
@login_required
def organizer_events():
    if not (current_user.is_organizer() or current_user.is_admin()):
        abort(403)
    
    events = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.start_time.desc()).all()
    return render_template('organizer/events.html', events=events)

@app.route('/organizer/check-in/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event_check_in(event_id):
    if not (current_user.is_organizer() or current_user.is_admin()):
        abort(403)
    
    event = Event.query.get_or_404(event_id)
    
    # Verify the current user is the organizer of this event
    if event.organizer_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    form = CheckInForm()
    form.event_id.data = event_id
    
    if form.validate_on_submit():
        full_name = form.full_name.data
        
        # Find the user with this full name
        users = User.query.all()
        matching_user = None
        
        for user in users:
            if user.get_full_name().lower() == full_name.lower():
                matching_user = user
                break
        
        if not matching_user:
            flash('No user found with that name', 'danger')
            return redirect(url_for('event_check_in', event_id=event_id))
        
        # Check if user is registered for this event
        registration = Registration.query.filter_by(user_id=matching_user.id, event_id=event_id).first()
        if not registration:
            flash('This user is not registered for this event', 'warning')
            return redirect(url_for('event_check_in', event_id=event_id))
        
        # Check if user already checked in
        existing_attendance = Attendance.query.filter_by(user_id=matching_user.id, event_id=event_id).first()
        if existing_attendance:
            flash('This user has already checked in', 'info')
            return redirect(url_for('event_check_in', event_id=event_id))
        
        # Create attendance record
        attendance = Attendance(user_id=matching_user.id, event_id=event_id)
        db.session.add(attendance)
        db.session.commit()
        
        flash(f'{matching_user.get_full_name()} has been checked in successfully!', 'success')
        return redirect(url_for('event_check_in', event_id=event_id))
    
    # Get list of registered users for this event
    registrations = Registration.query.filter_by(event_id=event_id).all()
    registered_users = [reg.user for reg in registrations]
    
    # Get list of users who have already checked in
    attendances = Attendance.query.filter_by(event_id=event_id).all()
    checked_in_users = [att.user for att in attendances]
    
    # Generate QR code for check-in if it doesn't exist
    qr_filename = f"event_{event_id}_checkin.png"
    qr_path = os.path.join('static', 'uploads', 'qrcodes', qr_filename)
    
    if not os.path.exists(qr_path):
        # Generate QR code data (URL to check-in page with event ID)
        qr_data = url_for('event_qr_check_in', event_id=event_id, _external=True)
        qr_image_path = generate_qr_code(qr_data, qr_filename)
    else:
        qr_image_path = os.path.join('uploads', 'qrcodes', qr_filename)
    
    return render_template('organizer/check_in.html', 
                          event=event, 
                          form=form,
                          registered_users=registered_users,
                          checked_in_users=checked_in_users,
                          qr_image_path=qr_image_path)

# QR code check-in route
@app.route('/events/<int:event_id>/qr-check-in', methods=['GET', 'POST'])
def event_qr_check_in(event_id):
    # Get event
    event = Event.query.get_or_404(event_id)
    
    # If user is logged in and registered for this event, check them in
    if current_user.is_authenticated:
        # Check if user is registered for this event
        registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if not registration:
            flash('You are not registered for this event', 'warning')
            return redirect(url_for('event_detail', event_id=event_id))
        
        # Check if user already checked in
        existing_attendance = Attendance.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if existing_attendance:
            flash('You have already checked in to this event', 'info')
            return redirect(url_for('event_detail', event_id=event_id))
        
        # Create attendance record
        attendance = Attendance(user_id=current_user.id, event_id=event_id)
        db.session.add(attendance)
        db.session.commit()
        
        flash('You have been checked in successfully!', 'success')
        return redirect(url_for('event_detail', event_id=event_id))
    else:
        # If not logged in, redirect to login page
        flash('Please log in to check in to this event', 'info')
        return redirect(url_for('login', next=url_for('event_qr_check_in', event_id=event_id)))

# Export participants route
@app.route('/organizer/events/<int:event_id>/export-participants')
@login_required
def export_participants(event_id):
    # Check if user is an organizer or admin
    if not current_user.is_organizer() and not current_user.is_admin():
        flash('You do not have permission to access this feature', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get event
    event = Event.query.get_or_404(event_id)
    
    # Check if user is the event organizer or an admin
    if event.organizer_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to export data for this event', 'danger')
        return redirect(url_for('dashboard'))
    
    # Export participant list
    from utils import export_participant_list
    export_path = export_participant_list(event_id)
    
    if export_path:
        flash('Participant list has been exported successfully', 'success')
        return redirect(url_for('static', filename=export_path))
    else:
        flash('Failed to export participant list', 'danger')
        return redirect(url_for('event_check_in', event_id=event_id))

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    # Get upcoming events the student is registered for
    user_registrations = Registration.query.filter_by(user_id=current_user.id).all()
    registered_event_ids = [reg.event_id for reg in user_registrations]
    
    upcoming_registered_events = Event.query.filter(
        Event.id.in_(registered_event_ids),
        Event.start_time > datetime.now()
    ).order_by(Event.start_time).limit(5).all()
    
    # Get all events for statistics
    all_events = Event.query.all()
    user_stats = get_user_events_stats(current_user.id, all_events, user_registrations)
    
    # Get recommended events (events in the next week that the user isn't registered for)
    next_week = datetime.now() + timedelta(days=7)
    recommended_events = Event.query.filter(
        ~Event.id.in_(registered_event_ids) if registered_event_ids else True,
        Event.start_time > datetime.now(),
        Event.start_time < next_week
    ).order_by(Event.start_time).limit(3).all()
    
    return render_template('student/dashboard.html', 
                          upcoming_events=upcoming_registered_events,
                          user_stats=user_stats,
                          recommended_events=recommended_events)

@app.route('/student/my-events')
@login_required
def my_events():
    # Get all registrations for the current user
    registrations = Registration.query.filter_by(user_id=current_user.id).all()
    registered_event_ids = [reg.event_id for reg in registrations]
    
    # Get all events the user is registered for
    registered_events = Event.query.filter(Event.id.in_(registered_event_ids)).all() if registered_event_ids else []
    
    # Separate into upcoming and past events
    upcoming_events = [event for event in registered_events if event.is_upcoming()]
    past_events = [event for event in registered_events if event.is_past()]
    
    # Get attendance records
    attendances = Attendance.query.filter_by(user_id=current_user.id).all()
    attended_event_ids = [att.event_id for att in attendances]
    
    # Get events the user has rated
    ratings = Rating.query.filter_by(user_id=current_user.id).all()
    rated_events = {rating.event_id: rating for rating in ratings}
    
    return render_template('student/my_events.html',
                          upcoming_events=upcoming_events,
                          past_events=past_events,
                          attended_event_ids=attended_event_ids,
                          rated_events=rated_events)

# Event routes
@app.route('/events')
def events_list():
    form = EventSearchForm()
    
    # Handle search/filter
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    
    # Base query
    events_query = Event.query
    
    # Apply filters
    if query:
        events_query = events_query.filter(Event.title.ilike(f'%{query}%') | Event.description.ilike(f'%{query}%'))
    
    if category:
        events_query = events_query.filter(Event.category == category)
    
    # Get upcoming and past events
    upcoming_events = events_query.filter(Event.start_time > datetime.now()).order_by(Event.start_time).all()
    past_events = events_query.filter(Event.start_time <= datetime.now()).order_by(Event.start_time.desc()).all()
    
    # Get all categories for filter dropdown
    categories = sorted(set([event.category for event in Event.query.all()]))
    
    return render_template('events/list.html', 
                          upcoming_events=upcoming_events, 
                          past_events=past_events,
                          form=form,
                          query=query,
                          selected_category=category,
                          categories=categories)

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if not (current_user.is_organizer() or current_user.is_admin()):
        abort(403)
    
    form = EventForm()
    
    # Populate the club selection dropdown
    clubs = Club.query.all()
    form.club_id.choices = [(club.id, club.name) for club in clubs]
    
    if form.validate_on_submit():
        poster_file = None
        if form.poster.data:
            poster_file = save_file(form.poster.data, 'uploads/event_posters')
        
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            category=form.category.data,
            max_participants=form.max_participants.data,
            poster=poster_file,
            organizer_id=current_user.id,
            club_id=form.club_id.data
        )
        
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events_list'))
    
    return render_template('events/create.html', form=form)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current user is registered
    is_registered = False
    can_rate = False
    user_rating = None
    
    if current_user.is_authenticated:
        registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        is_registered = registration is not None
        
        # Check if user has attended and can rate
        attendance = Attendance.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        can_rate = attendance is not None and event.is_past()
        
        # Get user's rating if exists
        user_rating = Rating.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    # Get event ratings
    ratings = Rating.query.filter_by(event_id=event_id).all()
    avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
    
    # Get number of registrations
    registrations_count = Registration.query.filter_by(event_id=event_id).count()
    
    # Get number of attendees
    attendance_count = Attendance.query.filter_by(event_id=event_id).count()
    
    # Rating form
    rating_form = RatingForm()
    if user_rating:
        rating_form.rating.data = user_rating.rating
        rating_form.feedback.data = user_rating.feedback
    
    return render_template('events/detail.html', 
                          event=event,
                          is_registered=is_registered,
                          can_rate=can_rate,
                          user_rating=user_rating,
                          rating_form=rating_form,
                          ratings=ratings,
                          avg_rating=avg_rating,
                          registrations_count=registrations_count,
                          attendance_count=attendance_count)

@app.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current user is the organizer or an admin
    if event.organizer_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    form = EventForm()
    
    # Populate the club selection dropdown
    clubs = Club.query.all()
    form.club_id.choices = [(club.id, club.name) for club in clubs]
    
    if form.validate_on_submit():
        if form.poster.data:
            poster_file = save_file(form.poster.data, 'uploads/event_posters')
            event.poster = poster_file
        
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.location = form.location.data
        event.category = form.category.data
        event.max_participants = form.max_participants.data
        event.club_id = form.club_id.data
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    
    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
        form.location.data = event.location
        form.category.data = event.category
        form.max_participants.data = event.max_participants
        form.club_id.data = event.club_id
    
    return render_template('events/edit.html', form=form, event=event)

@app.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current user is the organizer or an admin
    if event.organizer_id != current_user.id and not current_user.is_admin():
        abort(403)
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events_list'))

@app.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if event has already started
    if event.start_time <= datetime.now():
        flash('Registration is closed for this event', 'warning')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Check if user is already registered
    existing_registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing_registration:
        flash('You are already registered for this event', 'info')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Check if event has max participants limit
    if event.max_participants:
        current_registrations = Registration.query.filter_by(event_id=event_id).count()
        if current_registrations >= event.max_participants:
            flash('This event has reached maximum capacity', 'warning')
            return redirect(url_for('event_detail', event_id=event_id))
    
    # Create registration
    registration = Registration(user_id=current_user.id, event_id=event_id)
    db.session.add(registration)
    db.session.commit()
    
    flash('You have successfully registered for this event!', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/events/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister_from_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if event has already started
    if event.start_time <= datetime.now():
        flash('Cannot unregister from an event that has already started', 'warning')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Find registration
    registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not registration:
        flash('You are not registered for this event', 'info')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Delete registration
    db.session.delete(registration)
    db.session.commit()
    
    flash('You have successfully unregistered from this event', 'success')
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/events/<int:event_id>/rate', methods=['POST'])
@login_required
def rate_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if event has ended
    if not event.is_past():
        flash('You can only rate events that have ended', 'warning')
        return redirect(url_for('event_detail', event_id=event_id))
    
    # Check if user attended the event
    attendance = Attendance.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not attendance:
        flash('You can only rate events you have attended', 'warning')
        return redirect(url_for('event_detail', event_id=event_id))
    
    form = RatingForm()
    
    if form.validate_on_submit():
        # Check if user has already rated
        existing_rating = Rating.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = form.rating.data
            existing_rating.feedback = form.feedback.data
        else:
            # Create new rating
            rating = Rating(
                user_id=current_user.id,
                event_id=event_id,
                rating=form.rating.data,
                feedback=form.feedback.data
            )
            db.session.add(rating)
        
        db.session.commit()
        flash('Your rating has been submitted', 'success')
    
    return redirect(url_for('event_detail', event_id=event_id))

@app.route('/events/calendar')
def events_calendar():
    events = Event.query.all()
    return render_template('events/calendar.html', events=events)

@app.route('/api/events-calendar')
def events_calendar_data():
    events = Event.query.all()
    calendar_events = []
    
    for event in events:
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'url': url_for('event_detail', event_id=event.id)
        })
    
    return jsonify(calendar_events)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
