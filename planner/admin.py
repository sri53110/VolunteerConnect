from django.contrib import admin
from .models import Profile, Zone, Event, Shift, Signup, Announcement, AuditLog
admin.site.register(Profile)
admin.site.register(Zone)
admin.site.register(Event)
admin.site.register(Shift)
admin.site.register(Signup)
admin.site.register(Announcement)
admin.site.register(AuditLog)
