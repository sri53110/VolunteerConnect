from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from .models import Profile, Event, Zone, Shift, Signup
from .forms import ShiftForm

class ShiftRulesTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user("volunteer",password="SafePass123!")
        Profile.objects.create(user=self.user,role="VOLUNTEER")
        self.staff=User.objects.create_user("organizer",password="SafePass123!")
        Profile.objects.create(user=self.staff,role="ORGANIZER")
        now=timezone.now()
        self.event=Event.objects.create(title="Community Day",description="Test",venue="Town Hall",
            starts_at=now+timedelta(days=1),ends_at=now+timedelta(days=1,hours=4),created_by=self.staff)
        self.zone=Zone.objects.create(name="Registration")
        self.shift=Shift.objects.create(event=self.event,zone=self.zone,title="Welcome Desk",
            starts_at=now+timedelta(days=1),ends_at=now+timedelta(days=1,hours=2),capacity=1)
    def test_capacity_property(self):
        self.assertEqual(self.shift.vacancies,1)
        Signup.objects.create(shift=self.shift,volunteer=self.user,status="APPROVED")
        self.assertEqual(self.shift.vacancies,0)
    def test_shift_end_must_be_after_start(self):
        form = ShiftForm(data={
            "event":self.event.pk,
            "zone":self.zone.pk,
            "title":"Invalid time range",
            "description":"Test",
            "starts_at":"2030-01-02T10:00",
            "ends_at":"2030-01-02T09:00",
            "capacity":1,
            "status":"OPEN",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ends_at", form.errors)
    def test_shift_date_fields_use_datetime_local_inputs(self):
        form = ShiftForm()
        self.assertEqual(form.fields["starts_at"].widget.input_type, "datetime-local")
        self.assertEqual(form.fields["starts_at"].widget.format, "%Y-%m-%dT%H:%M")
        self.assertEqual(form.fields["ends_at"].label, "End date and time")
    def test_volunteer_can_mark_approved_shift_complete(self):
        signup = Signup.objects.create(
            shift=self.shift,
            volunteer=self.user,
            status="APPROVED",
        )
        self.client.force_login(self.user)

        response = self.client.post(f"/signups/{signup.pk}/complete/")

        signup.refresh_from_db()
        self.assertRedirects(response, "/dashboard/")
        self.assertEqual(signup.status, "COMPLETED")
        self.assertIsNotNone(signup.completed_at)
    def test_dashboard_shows_volunteers_completed_shift_count(self):
        Signup.objects.create(
            shift=self.shift,
            volunteer=self.user,
            status="COMPLETED",
            completed_at=timezone.now(),
        )
        self.client.force_login(self.user)

        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["completed_shifts_count"], 1)
        self.assertContains(response, "Completed shifts")
    def test_dashboard_offers_complete_button_for_approved_application(self):
        signup = Signup.objects.create(
            shift=self.shift,
            volunteer=self.user,
            status="APPROVED",
        )
        self.client.force_login(self.user)

        response = self.client.get("/dashboard/")

        self.assertContains(response, "Mark shift completed")
        self.assertContains(response, f'action="/signups/{signup.pk}/complete/"')
    def test_application_history_hides_withdrawn_application_without_deleting_it(self):
        signup = Signup.objects.create(
            shift=self.shift,
            volunteer=self.user,
            status="WITHDRAWN",
        )
        self.client.force_login(self.user)

        response = self.client.get("/applications/history/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Application history")
        self.assertContains(response, "No active or completed applications to show.")
        self.assertNotContains(response, self.shift.title)
        signup.refresh_from_db()
        self.assertEqual(signup.status, "WITHDRAWN")
    def test_dashboard_hides_withdrawn_applications(self):
        signup = Signup.objects.create(
            shift=self.shift,
            volunteer=self.user,
            status="WITHDRAWN",
        )
        self.client.force_login(self.user)

        response = self.client.get("/dashboard/")

        self.assertEqual(response.context["signups"].count(), 0)
        self.assertNotContains(response, "status-withdrawn")
        signup.refresh_from_db()
        self.assertEqual(signup.status, "WITHDRAWN")
    def test_application_history_only_shows_signed_in_volunteers_applications(self):
        other_volunteer = User.objects.create_user("history-other-volunteer", password="test-password")
        Signup.objects.create(shift=self.shift, volunteer=other_volunteer, status="WITHDRAWN")
        self.client.force_login(self.user)

        response = self.client.get("/applications/history/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No active or completed applications to show.")
        self.assertNotContains(response, self.shift.title)
    def test_volunteer_cannot_complete_another_volunteers_shift(self):
        other_volunteer = User.objects.create_user("other-volunteer", password="test-password")
        signup = Signup.objects.create(
            shift=self.shift,
            volunteer=other_volunteer,
            status="APPROVED",
        )
        self.client.force_login(self.user)

        response = self.client.post(f"/signups/{signup.pk}/complete/")

        self.assertEqual(response.status_code, 404)
        signup.refresh_from_db()
        self.assertEqual(signup.status, "APPROVED")
        self.assertIsNone(signup.completed_at)
    def test_non_post_request_does_not_complete_shift(self):
        signup = Signup.objects.create(
            shift=self.shift,
            volunteer=self.user,
            status="APPROVED",
        )
        self.client.force_login(self.user)

        response = self.client.get(f"/signups/{signup.pk}/complete/")

        self.assertRedirects(response, "/dashboard/")
        signup.refresh_from_db()
        self.assertEqual(signup.status, "APPROVED")
        self.assertIsNone(signup.completed_at)

class DemoDataCommandTests(TestCase):
    def test_seed_command_creates_upcoming_shifts_without_duplicates(self):
        call_command("seed_demo_data", stdout=None)
        call_command("seed_demo_data", stdout=None)

        shifts = Shift.objects.filter(
            event__created_by__username="volunteerconnect-demo-organizer",
            status="OPEN",
            starts_at__gte=timezone.now(),
        )
        self.assertEqual(shifts.count(), 44)
