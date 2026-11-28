from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from functools import wraps
from .models import Event, Shift, Signup, Zone, Announcement, AuditLog
from .forms import RegisterForm, EventForm, ShiftForm, ZoneForm, AnnouncementForm

def role_of(user):
    if user.is_superuser: return "ADMIN"
    return getattr(getattr(user, "profile", None), "role", "VOLUNTEER")

def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if role_of(request.user) not in ("ADMIN","ORGANIZER","ZONE_LEAD"):
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view(request, *args, **kwargs)
    return wrapped

def log_action(user, action, obj=None, details=""):
    AuditLog.objects.create(actor=user, action=action, object_type=obj.__class__.__name__ if obj else "System",
                            object_id=obj.pk if obj else None, details=details)

def home(request):
    events = Event.objects.filter(published=True, ends_at__gte=timezone.now())[:6]
    shifts = Shift.objects.filter(status="OPEN", event__published=True, starts_at__gte=timezone.now()).select_related("event","zone")[:6]
    return render(request, "planner/home.html", {"events":events,"shifts":shifts})

def register_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created. Welcome to VolunteerConnect!")
        return redirect("dashboard")
    return render(request, "planner/register.html", {"form":form})

@login_required
def dashboard(request):
    role = role_of(request.user)
    if role in ("ADMIN","ORGANIZER","ZONE_LEAD"): return redirect("admin_dashboard")
    signups = Signup.objects.filter(volunteer=request.user).exclude(status="WITHDRAWN").select_related("shift","shift__event","shift__zone")
    open_shifts = Shift.objects.filter(status="OPEN", event__published=True, starts_at__gte=timezone.now()).select_related("event","zone")[:8]
    announcements = Announcement.objects.filter(active=True)[:5]
    completed_shifts_count = signups.filter(status="COMPLETED").count()
    return render(request, "planner/dashboard.html", {"signups":signups,"open_shifts":open_shifts,"announcements":announcements,"completed_shifts_count":completed_shifts_count})

@login_required
def application_history(request):
    signups = Signup.objects.filter(volunteer=request.user).exclude(status="WITHDRAWN").select_related(
        "shift", "shift__event", "shift__zone"
    )
    return render(request, "planner/application_history.html", {"signups":signups})

@login_required
def shift_list(request):
    shifts = Shift.objects.filter(status="OPEN", event__published=True, starts_at__gte=timezone.now()).select_related("event","zone")
    q = request.GET.get("q","").strip()
    if q: shifts = shifts.filter(Q(title__icontains=q)|Q(event__title__icontains=q)|Q(zone__name__icontains=q))
    return render(request, "planner/shifts.html", {"shifts":shifts,"q":q})

@login_required
@transaction.atomic
def apply_shift(request, shift_id):
    if request.method != "POST": return redirect("shift_list")
    shift = get_object_or_404(Shift.objects.select_for_update(), pk=shift_id, status="OPEN")
    if role_of(request.user) != "VOLUNTEER":
        messages.error(request, "Only volunteer accounts can apply for shifts.")
        return redirect("shift_list")
    if shift.vacancies <= 0:
        messages.error(request, "This shift has reached its capacity.")
        return redirect("shift_list")
    overlap = Signup.objects.filter(volunteer=request.user, status="APPROVED",
        shift__starts_at__lt=shift.ends_at, shift__ends_at__gt=shift.starts_at).exists()
    if overlap:
        messages.error(request, "This shift overlaps with one of your approved assignments.")
        return redirect("shift_list")
    signup, created = Signup.objects.get_or_create(shift=shift, volunteer=request.user)
    if not created and signup.status != "WITHDRAWN":
        messages.warning(request, "You already have an application for this shift.")
    else:
        signup.status = "PENDING"; signup.save()
        log_action(request.user, "Applied for shift", shift)
        messages.success(request, "Application submitted. It is waiting for organizer approval.")
    return redirect("dashboard")

@login_required
def withdraw_signup(request, signup_id):
    signup = get_object_or_404(Signup, pk=signup_id, volunteer=request.user)
    if request.method == "POST" and signup.status in ("PENDING","APPROVED"):
        signup.status = "WITHDRAWN"; signup.save()
        log_action(request.user, "Withdrew from shift", signup.shift)
        messages.success(request, "Your application was withdrawn.")
    return redirect("dashboard")

@login_required
def complete_signup(request, signup_id):
    signup = get_object_or_404(
        Signup.objects.select_related("shift"),
        pk=signup_id,
        volunteer=request.user,
    )
    if request.method == "POST" and signup.status == "APPROVED":
        signup.status = "COMPLETED"
        signup.completed_at = timezone.now()
        signup.save(update_fields=["status", "completed_at", "updated_at"])
        log_action(request.user, "Completed shift", signup.shift)
        messages.success(request, "Shift marked complete.")
    elif signup.status != "COMPLETED":
        messages.error(request, "Only approved shifts can be marked complete.")
    return redirect("dashboard")

@staff_required
def admin_dashboard(request):
    context = {
        "users_count":User.objects.count(), "events_count":Event.objects.count(),
        "shifts_count":Shift.objects.count(), "pending_count":Signup.objects.filter(status="PENDING").count(),
        "signups":Signup.objects.select_related("volunteer","shift","shift__event").order_by("-applied_at")[:12],
        "shifts":Shift.objects.select_related("event","zone").order_by("-created_at")[:8],
        "logs":AuditLog.objects.select_related("actor")[:10],
        "announcements":Announcement.objects.filter(active=True)[:5],
    }
    return render(request, "planner/admin_dashboard.html", context)

@staff_required
def manage_events(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False); event.created_by = request.user; event.save()
        log_action(request.user, "Created event", event); messages.success(request,"Event created.")
        return redirect("manage_events")
    return render(request,"planner/manage_events.html",{"form":form,"events":Event.objects.all()})

@staff_required
def manage_shifts(request):
    form = ShiftForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        shift = form.save(); log_action(request.user,"Created shift",shift)
        messages.success(request,"Shift created."); return redirect("manage_shifts")
    return render(request,"planner/manage_shifts.html",{"form":form,"shifts":Shift.objects.select_related("event","zone")})

@staff_required
def manage_zones(request):
    form = ZoneForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        zone = form.save(); log_action(request.user,"Created zone",zone)
        messages.success(request,"Zone created."); return redirect("manage_zones")
    return render(request,"planner/manage_zones.html",{"form":form,"zones":Zone.objects.all()})

@staff_required
def review_signup(request, signup_id, decision):
    signup = get_object_or_404(Signup.objects.select_related("shift"), pk=signup_id)
    if request.method == "POST" and decision in ("approve","reject"):
        if decision == "approve":
            shift = Shift.objects.select_for_update().get(pk=signup.shift_id)
            if shift.vacancies <= 0:
                messages.error(request,"No vacancies remain for this shift.")
                return redirect("admin_dashboard")
            conflict = Signup.objects.filter(volunteer=signup.volunteer,status="APPROVED",
                shift__starts_at__lt=shift.ends_at,shift__ends_at__gt=shift.starts_at).exclude(pk=signup.pk).exists()
            if conflict:
                messages.error(request,"Cannot approve: volunteer has an overlapping approved shift.")
                return redirect("admin_dashboard")
            signup.status="APPROVED"
        else: signup.status="REJECTED"
        signup.save(); log_action(request.user,f"{decision.title()}d signup",signup.shift, f"Volunteer: {signup.volunteer.username}")
        messages.success(request,f"Application {decision}d.")
    return redirect("admin_dashboard")

@staff_required
def manage_announcements(request):
    form = AnnouncementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item=form.save(commit=False); item.created_by=request.user; item.save()
        log_action(request.user,"Published announcement",item); messages.success(request,"Announcement published.")
        return redirect("manage_announcements")
    return render(request,"planner/announcements.html",{"form":form,"items":Announcement.objects.all()})

@login_required
def live_status(request):
    data = {"server_time":timezone.now().isoformat(),
            "pending":Signup.objects.filter(status="PENDING").count(),
            "open_shifts":Shift.objects.filter(status="OPEN").count()}
    return JsonResponse(data)
