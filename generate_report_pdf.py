from fpdf import FPDF
import os

report_content = '''
Campus Event Management System (CampusEventHub)
Comprehensive Technical and User Documentation

1. Executive Summary
CampusEventHub is a robust, full-featured web application designed to facilitate the management, organization, and participation in campus events. The platform supports multiple user roles—Administrators, Organizers, and Students—each with tailored dashboards and permissions. The system streamlines event creation, registration, check-in (including QR code support), analytics, and participant export, providing a modern, secure, and user-friendly experience for all stakeholders.

2. Project Objectives
- Centralization: Provide a single platform for all campus event activities.
- Efficiency: Automate and simplify event management, registration, and attendance tracking.
- Accessibility: Ensure all users (students, organizers, admins) have intuitive access to relevant features.
- Security: Enforce role-based access control and secure data handling.
- Scalability: Design the system to be easily extensible for future features or larger deployments.

3. System Architecture
3.1. Technology Stack
- Backend: Python 3.11+, Flask, Flask-Login, Flask-WTF, SQLAlchemy
- Frontend: HTML5, CSS3, Bootstrap 5, Jinja2, JavaScript (ES6+), FullCalendar.js, Chart.js
- Database: SQLite (default, easily switchable to PostgreSQL/MySQL)
- Other Libraries: qrcode (QR code generation), pandas & openpyxl (Excel export), Pillow (image processing)
- Deployment: Gunicorn (production server), Nginx (optional for reverse proxy), pip/venv for dependency management

3.2. Directory Structure
(Insert directory tree as shown in previous message)

4. Detailed Functionality and Code Explanation
(Insert all code explanations and function summaries as in previous message)

5. User Guide
(Insert user guide for Students, Organizers, and Administrators)

6. Developer Guide: Running the Project on Your Own Laptop
(Insert all steps, commands, and environment variable notes)

7. Security and Best Practices
(Insert security notes)

8. Extensibility and Customization
(Insert extensibility notes)

9. Troubleshooting
(Insert troubleshooting notes)

10. Contact and Support
(Insert contact info)

11. Conclusion
(Insert conclusion)

12. System Diagrams
- High-Level Architecture Diagram: (Insert diagram as text or add as image later)
- Entity-Relationship Diagram (ERD): (Insert diagram as text or add as image later)

13. Screenshots
(Add screenshots of login, dashboards, event detail, check-in, export, etc. as needed)

14. API Documentation (for future extensibility)
(Insert sample API endpoints and responses)

15. Example User Stories
(Insert user stories)

16. Example Test Cases
(Insert test cases)

17. Deployment and Maintenance
(Insert deployment and maintenance notes)

18. Acknowledgements
(Insert acknowledgements)

19. Contact and Support
(Insert contact info again for emphasis)

20. Appendix
- Sample Data
- Change Log
- License

(You can now add more content, screenshots, or diagrams as needed!)
'''

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Campus Event Management System (CampusEventHub)', ln=True, align='C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Use a Unicode font (DejaVu) if available, else fallback to Arial
font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
if os.path.exists(font_path):
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.set_font('DejaVu', '', 11)
else:
    pdf.set_font('Arial', '', 11)

line_count = 0
for line in report_content.split('\n'):
    if line.strip().startswith(tuple(f'{i}.' for i in range(1, 21))):
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, line.strip(), ln=True)
        if os.path.exists(font_path):
            pdf.set_font('DejaVu', '', 11)
        else:
            pdf.set_font('Arial', '', 11)
        line_count += 2
    elif line.strip().startswith('- '):
        pdf.cell(10)
        pdf.multi_cell(0, 8, line.strip())
        line_count += 1
    elif line.strip() == '':
        pdf.ln(2)
        line_count += 1
    else:
        pdf.multi_cell(0, 8, line.strip())
        line_count += 1
    if line_count > 40:
        pdf.add_page()
        line_count = 0

pdf.output('CampusEventHub_Project_Report.pdf')
print('PDF report generated: CampusEventHub_Project_Report.pdf') 