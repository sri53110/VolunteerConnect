# VolunteerConnect – Live Shift Planner

A Django web application for community organisations to coordinate volunteers, events, zones, shift applications and live schedule updates.

## Included modules
- Public landing page and upcoming opportunity cards
- Volunteer / Organizer registration and login
- Role-aware volunteer dashboard
- Shift discovery, applications and withdrawal
- Organizer management dashboard
- Event, shift, zone and announcement creation
- Application approval / rejection workflow
- Capacity and overlapping-shift checks
- Audit trail and live status polling endpoint
- Django admin interface and automated starter tests

## Requirements
- Python 3.10+
- pip

## Windows setup (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py seed_demo_data
py manage.py runserver