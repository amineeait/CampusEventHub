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
        
        # Always return a web-compatible path (forward slashes)
        return os.path.join(folder, unique_filename).replace('\\', '/').replace('\\', '/')
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

def generate_qr_code(data, filename=None):
    """Generate QR code from data and save to static/uploads/qrcodes"""
    import qrcode
    import os
    from flask import current_app
    
    # Create QR code with simplified API
    img = qrcode.make(data)
    
    # Create directory if it doesn't exist
    qr_code_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'qrcodes')
    os.makedirs(qr_code_dir, exist_ok=True)
    
    # Save the image
    if filename:
        file_path = os.path.join(qr_code_dir, filename)
    else:
        file_path = os.path.join(qr_code_dir, f"{uuid.uuid4().hex}.png")
    
    img.save(file_path)
    
    # Return the relative path for use in templates
    return os.path.join('uploads', 'qrcodes', os.path.basename(file_path)).replace('\\', '/').replace('\\', '/')

def export_participant_list(event_id, format='excel'):
    """Export participant list to Excel or CSV format"""
    import pandas as pd
    import os
    from flask import current_app
    from models import Event, Registration, User, Attendance
    
    # Get event and registrations
    event = Event.query.get(event_id)
    if not event:
        return None
    
    # Create directory if it doesn't exist
    export_dir = os.path.join(current_app.root_path, 'static', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    # Get registrations and attendances
    registrations = Registration.query.filter_by(event_id=event_id).all()
    attendances = Attendance.query.filter_by(event_id=event_id).all()
    attended_user_ids = [attendance.user_id for attendance in attendances]
    
    # Prepare data for export
    data = []
    for registration in registrations:
        user = User.query.get(registration.user_id)
        if user:
            data.append({
                'ID': user.id,
                'First Name': user.first_name,
                'Last Name': user.last_name,
                'Email': user.email,
                'Registration Date': registration.registration_time.strftime('%Y-%m-%d %H:%M'),
                'Attended': 'Yes' if user.id in attended_user_ids else 'No'
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to Excel
    filename = f"event_{event_id}_participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(export_dir, filename)
    df.to_excel(file_path, index=False)
    
    # Return the relative path for download
    return os.path.join('exports', filename)
