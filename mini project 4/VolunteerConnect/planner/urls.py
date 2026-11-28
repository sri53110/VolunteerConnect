from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
 path("",views.home,name="home"),
 path("register/",views.register_view,name="register"),
 path("login/",auth_views.LoginView.as_view(template_name="planner/login.html"),name="login"),
 path("logout/",auth_views.LogoutView.as_view(),name="logout"),
 path("dashboard/",views.dashboard,name="dashboard"),
 path("applications/history/",views.application_history,name="application_history"),
 path("shifts/",views.shift_list,name="shift_list"),
 path("shifts/<int:shift_id>/apply/",views.apply_shift,name="apply_shift"),
 path("signups/<int:signup_id>/withdraw/",views.withdraw_signup,name="withdraw_signup"),
 path("signups/<int:signup_id>/complete/",views.complete_signup,name="complete_signup"),
 path("control/",views.admin_dashboard,name="admin_dashboard"),
 path("control/events/",views.manage_events,name="manage_events"),
 path("control/shifts/",views.manage_shifts,name="manage_shifts"),
 path("control/zones/",views.manage_zones,name="manage_zones"),
 path("control/signups/<int:signup_id>/<str:decision>/",views.review_signup,name="review_signup"),
 path("control/announcements/",views.manage_announcements,name="manage_announcements"),
 path("api/live-status/",views.live_status,name="live_status"),
]
