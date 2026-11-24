from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Event, Shift, Zone, Announcement

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20, required=False)
    role = forms.ChoiceField(choices=[("VOLUNTEER","Volunteer"),("ORGANIZER","Organizer")])
    class Meta:
        model = User
        fields = ("username","first_name","email","phone","role","password1","password2")
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
            Profile.objects.create(user=user, role=self.cleaned_data["role"], phone=self.cleaned_data.get("phone",""))
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title","description","venue","starts_at","ends_at","published"]
        widgets = {"starts_at": forms.DateTimeInput(attrs={"type":"datetime-local"}), "ends_at": forms.DateTimeInput(attrs={"type":"datetime-local"})}

class ShiftForm(forms.ModelForm):
    starts_at = forms.DateTimeField(
        label="Start date and time",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )
    ends_at = forms.DateTimeField(
        label="End date and time",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Shift
        fields = ["event","zone","title","description","starts_at","ends_at","capacity","status"]

    def clean(self):
        cleaned_data = super().clean()
        starts_at = cleaned_data.get("starts_at")
        ends_at = cleaned_data.get("ends_at")
        if starts_at and ends_at and ends_at <= starts_at:
            self.add_error("ends_at", "End date and time must be after the start date and time.")
        return cleaned_data

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ["name","location","lead"]

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title","message","active"]
