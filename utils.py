import os
import uuid
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

def save_file(file, folder):
    """Save a file to the specified folder and return the filename"""
    if file and file.filename:
        # Create unique filename
        filename = secure_filename(file.filename)
        _, file_extension = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Ensure folder exists
        upload_path = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return os.path.join(folder, unique_filename)
    return None

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format a datetime object to string"""
    if value:
        return value.strftime(format)
    return ""

def get_event_stats(events):
    """Get statistics for a list of events"""
    total_events = len(events)
    upcoming_events = sum(1 for event in events if event.is_upcoming())
    past_events = sum(1 for event in events if event.is_past())
    ongoing_events = sum(1 for event in events if event.is_ongoing())
    
    categories = {}
    for event in events:
        if event.category in categories:
            categories[event.category] += 1
        else:
            categories[event.category] = 1
    
    return {
        'total': total_events,
        'upcoming': upcoming_events,
        'past': past_events,
        'ongoing': ongoing_events,
        'categories': categories
    }

def get_user_events_stats(user_id, events, registrations):
    """Get statistics for a user's events"""
    registered_events = [reg.event_id for reg in registrations]
    registered_count = len(registered_events)
    
    upcoming_registered = sum(1 for event in events if event.id in registered_events and event.is_upcoming())
    past_registered = sum(1 for event in events if event.id in registered_events and event.is_past())
    
    return {
        'registered_count': registered_count,
        'upcoming_registered': upcoming_registered,
        'past_registered': past_registered
    }

def allowed_file(filename, allowed_extensions):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_events_by_date_range(start_date, end_date, events):
    """Filter events by date range"""
    return [event for event in events if start_date <= event.start_time <= end_date]
