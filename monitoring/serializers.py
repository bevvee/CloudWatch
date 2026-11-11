from rest_framework import serializers
from .models import Reading,Incident,Comment,Notification
class ReadingSerializer(serializers.ModelSerializer):
 class Meta:
  model=Reading;fields=['id','temp','hum','created_at'];read_only_fields=['id','created_at']
 def validate_temp(self,value):
  if not -50<=value<=100:raise serializers.ValidationError('Température hors plage plausible')
  return value
class IncidentSerializer(serializers.ModelSerializer):
 class Meta:
  model=Incident;fields=['id','title','status','reading','created_at','acknowledged_at','resolved_at']
class CommentSerializer(serializers.ModelSerializer):
 username=serializers.CharField(source='user.username',read_only=True)
 class Meta:
  model=Comment;fields=['id','username','text','created_at']
class NotificationSerializer(serializers.ModelSerializer):
 class Meta:
  model=Notification;fields=['id','incident','seen','created_at']
