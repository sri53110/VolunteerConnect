from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = [("VOLUNTEER", "Volunteer"), ("ORGANIZER", "Organizer"), ("ZONE_LEAD", "Zone Lead"), ("ADMIN", "Administrator")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="VOLUNTEER")
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=120, blank=True)
    def __str__(self): return f"{self.user.username} - {self.role}"

class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=180, blank=True)
    lead = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="led_zones")
    def __str__(self): return self.name

class Event(models.Model):
    title = models.CharField(max_length=160)
    description = models.TextField()
    venue = models.CharField(max_length=180)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["starts_at"]
    def __str__(self): return self.title

class Shift(models.Model):
    STATUS = [("DRAFT","Draft"),("OPEN","Open"),("CLOSED","Closed")]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="shifts")
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, related_name="shifts")
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=10, choices=STATUS, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["starts_at"]
    def __str__(self): return f"{self.title} ({self.zone})"
    @property
    def approved_count(self):
        return self.signups.filter(status="APPROVED").count()
    @property
    def vacancies(self):
        return max(0, self.capacity - self.approved_count)

class Signup(models.Model):
    STATES = [("PENDING","Pending"),("APPROVED","Approved"),("COMPLETED","Completed"),("REJECTED","Rejected"),("WITHDRAWN","Withdrawn")]
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name="signups")
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shift_signups")
    status = models.CharField(max_length=12, choices=STATES, default="PENDING")
    completed_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["shift","volunteer"], name="unique_volunteer_shift")]
        ordering = ["-applied_at"]
    def __str__(self): return f"{self.volunteer} - {self.shift} - {self.status}"

class Announcement(models.Model):
    title = models.CharField(max_length=160)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return self.title

class AuditLog(models.Model):
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=80)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"{self.action} by {self.actor}"
