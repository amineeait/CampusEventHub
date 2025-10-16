🎓 CampusEventHub — Campus Event Management System
🧩 Overview

CampusEventHub is a scalable, full-featured web application designed to streamline campus event management. It empowers Administrators, Organizers, and Students with tailored dashboards, enabling smooth event creation, registration, attendance tracking (QR codes), analytics, and participant export.
The platform emphasizes modern design, security, and usability.

🚀 Key Features

🔐 Role-Based Access Control — Secure access for Admins, Organizers, and Students

📅 Interactive Event Calendar — Powered by FullCalendar.js

🧾 Event Registration & QR Check-in — Quick participant management

📊 Analytics Dashboard — Real-time insights using Chart.js

📤 Excel Export — Participant lists exportable via pandas & openpyxl

🖼️ Poster Uploads & Photo Management

📬 Event Reminders & Ratings — Post-event engagement

🏗️ System Architecture
🔧 Technology Stack
Layer	Technology
Backend	Python, Flask, Flask-Login, Flask-WTF, SQLAlchemy
Frontend	HTML5, CSS3, Bootstrap 5, Jinja2, JavaScript (ES6+), FullCalendar.js, Chart.js
Database	SQLite (default), PostgreSQL/MySQL (optional)
Other Libraries	qrcode, pandas, openpyxl, Pillow
Deployment	Gunicorn, Nginx (optional)
📁 Directory Structure
CampusEventHub/
├── app.py
├── main.py
├── config.py
├── models.py
├── forms.py
├── routes.py
├── utils.py
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│   └── exports/
├── templates/
│   ├── layout.html
│   ├── dashboard.html
│   ├── admin/
│   ├── organizer/
│   ├── student/
│   └── events/
└── requirements.txt

👥 User Roles
Administrator

Manage users, clubs, and system analytics

Full control over events and registrations

Organizer

Create and manage clubs and events

Check in participants via name or QR code

Export participant lists and view analytics

Student

Register and track events

Check in using QR code

Rate attended events

⚙️ Installation & Setup
🧱 Prerequisites

Python 3.11+

pip (Python package manager)

(Optional) PostgreSQL or MySQL

🪜 Steps
# 1. Clone the repository
git clone https://github.com/amineeait/CampusEventHub.git
cd CampusEventHub

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py

🧠 Core Modules

app.py — Initializes Flask app and database

models.py — SQLAlchemy ORM models (Users, Events, Clubs, Registrations, etc.)

routes.py — Flask routes (authentication, dashboards, events, etc.)

forms.py — WTForms with input validation

utils.py — Helper functions (QR code generation, Excel exports, etc.)

🔐 Security Highlights

Role-based access decorators

Secure session handling via Flask-Login

Input validation using WTForms

Safe file uploads (type restrictions)

Custom error pages (403, 404, 500)

🧩 Future Improvements

RESTful APIs for mobile apps

Advanced search and filtering

Push notifications for event reminders

Cloud storage integration for uploads

📸 Screenshots

Add visuals of your login page, dashboards, event pages, and analytics here.

📚 Learning Outcomes

This project strengthened my expertise in Flask development, database modeling, frontend-backend integration, and secure web architecture, deepening my understanding of full-stack system design.

👨‍💻 Developer

Mohamed Amine Ait El Mahjoub
🎓 Final-year Computer Science and Technology Student (GPA: 3.51)                                                             
📍 China Jiliang University
📧 mohamedamineaitelmahjoub@gmail.com

🔗 LinkedIn
 | GitHub

💬 “Learn, build, and innovate every day.”
