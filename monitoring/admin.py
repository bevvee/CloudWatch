from django.contrib import admin
from .models import Settings,Reading,Incident,Comment,Event,Notification
for model in (Settings,Reading,Incident,Comment,Event,Notification):admin.site.register(model)
