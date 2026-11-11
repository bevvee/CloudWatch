from django.db import transaction
from .models import Reading,Incident,Event,Notification,Settings
from django.contrib.auth.models import User
from django.conf import settings
from .ntfy_service import send_temperature_alert

def current_settings():
 obj=Settings.objects.first()
 if obj:return obj
 return Settings.objects.create(min_temp=settings.COLDWATCH_MIN_TEMP,max_temp=settings.COLDWATCH_MAX_TEMP,stale_minutes=settings.COLDWATCH_STALE_MINUTES)
@transaction.atomic
def record_measurement(validated):
 reading=Reading.objects.create(**validated)
 config=current_settings()
 if reading.temp<config.min_temp or reading.temp>config.max_temp:
  # A continuous excursion creates one active incident, not one incident per measurement.
  incident=Incident.objects.filter(status__in=[Incident.OPEN,Incident.ACK]).order_by('-created_at').first()
  if incident is None:
   incident=Incident.objects.create(reading=reading,title=f'Excursion de température : {reading.temp} °C')
   Event.objects.create(incident=incident,action='created',detail=f'Mesure {reading.id} : {reading.temp} °C; seuils {config.min_temp} à {config.max_temp} °C')
   operators=list(User.objects.filter(is_active=True,groups__name='Operateurs').distinct().order_by('id')[:3])
   Notification.objects.bulk_create([Notification(user=u,incident=incident) for u in operators])
   send_temperature_alert(reading.temp, reading.hum)
  else:
   Event.objects.create(incident=incident,action='excursion',detail=f'Mesure {reading.id} : {reading.temp} °C')
 return reading
