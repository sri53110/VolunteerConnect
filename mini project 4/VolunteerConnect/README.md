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
# 1. Extract the ZIP and open the project folder
cd VolunteerConnect

# 2. Create and activate virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
py -m pip install -r requirements.txt

# 4. Create database tables
py manage.py makemigrations planner
py manage.py migrate

# 5. Create administrator account
py manage.py createsuperuser

# 6. Add sample events and open shifts
py manage.py seed_demo_data

# 7. Start server
py manage.py runserver
```
Open http://127.0.0.1:8000/

The sample dataset includes future-dated community events and open shifts so the
shift search page has opportunities to display. Running `seed_demo_data` again
updates these records rather than adding duplicates.

## First-time data setup
1. Register a user with role Organizer.
2. Sign in and open Management.
3. Create a Zone.
4. Create an Event.
5. Create one or more Shifts.
6. Register a separate Volunteer account and apply for a shift.
7. Organizer approves/rejects the application in the management dashboard.

You can also use `/django-admin/` to manage all records.

## Roles
- Volunteer: browse shifts, apply, view and withdraw own applications.
- Organizer / Zone Lead: access management dashboard and create operational records.
- Administrator: Django superuser has full access.

Registration deliberately does not allow a public user to self-assign Administrator or Zone Lead.

## Tests
```powershell
py manage.py test
```

## Deployment notes
- Set `DJANGO_SECRET_KEY` to a long random secret.
- Set `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to your deployed hostnames.
- Configure a production database and static-file hosting for production.
- Do not commit `.env`, database files, passwords or secret keys.

## SRS alignment
The implementation follows the supplied SRS title and core requirements: role-based access, persistent relational data, capacity and overlap protection, shared-record workflows, live polling, audit records, and repeatable setup/tests.

## Current implementation boundaries
This starter uses polling for live status rather than WebSockets. Email/SMS delivery, external calendar integrations, payment gateways and private third-party APIs are not included. Organizer-created records are auditable; direct changes made in Django admin are not automatically added to the custom audit log.
