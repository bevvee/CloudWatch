from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
class Settings(models.Model):
 name=models.CharField(max_length=80,default='Enceinte principale',unique=True)
 min_temp=models.FloatField(default=2)
 max_temp=models.FloatField(default=8)
 stale_minutes=models.PositiveIntegerField(default=45)
 def __str__(self):return self.name
class Reading(models.Model):
 temp=models.FloatField();hum=models.FloatField(validators=[MinValueValidator(0),MaxValueValidator(100)])
 created_at=models.DateTimeField(auto_now_add=True,db_index=True)
 class Meta:ordering=['-created_at']
 def __str__(self):return f'{self.temp} °C / {self.hum}%'
class Incident(models.Model):
 OPEN='open';ACK='acknowledged';RESOLVED='resolved'
 STATUS=[(OPEN,'Ouvert'),(ACK,'Acquitté'),(RESOLVED,'Résolu')]
 reading=models.ForeignKey(Reading,on_delete=models.PROTECT,related_name='incidents')
 status=models.CharField(max_length=20,choices=STATUS,default=OPEN,db_index=True)
 title=models.CharField(max_length=200)
 created_at=models.DateTimeField(auto_now_add=True)
 acknowledged_at=models.DateTimeField(null=True,blank=True)
 acknowledged_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='acknowledged_incidents')
 resolved_at=models.DateTimeField(null=True,blank=True)
 resolved_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='resolved_incidents')
 class Meta:ordering=['-created_at']
class Comment(models.Model):
 incident=models.ForeignKey(Incident,on_delete=models.CASCADE,related_name='comments')
 user=models.ForeignKey(User,on_delete=models.PROTECT)
 text=models.TextField(max_length=2000)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:ordering=['created_at']
class Event(models.Model):
 incident=models.ForeignKey(Incident,on_delete=models.CASCADE,related_name='events')
 actor=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
 action=models.CharField(max_length=40)
 detail=models.TextField(blank=True)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:ordering=['created_at']
class Notification(models.Model):
 user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='coldwatch_notifications')
 incident=models.ForeignKey(Incident,on_delete=models.CASCADE)
 seen=models.BooleanField(default=False)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:ordering=['-created_at']
