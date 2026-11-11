from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import logout
from django.db.models import Q
from django.http import JsonResponse,HttpResponseForbidden
from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import generics,status
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from .models import Reading,Incident,Comment,Event,Notification,Settings
from .serializers import ReadingSerializer,IncidentSerializer,CommentSerializer,NotificationSerializer
from .services import record_measurement,current_settings

def operator(user):return user.is_authenticated and (user.is_staff or user.groups.filter(name='Operateurs').exists())
@login_required
def dashboard(request):
 latest=Reading.objects.first();config=current_settings()
 readings=list(Reading.objects.order_by('-created_at')[:8]);readings.reverse()
 active=Incident.objects.exclude(status=Incident.RESOLVED).count()
 stale=not latest or latest.created_at<timezone.now()-timedelta(minutes=config.stale_minutes)
 return render(request,'monitoring/dashboard.html',{'latest':latest,'config':config,'readings':readings,'chart_readings':[{'temp':r.temp,'hum':r.hum,'created_at':r.created_at.isoformat()} for r in readings],'active':active,'stale':stale,'incident_count':Incident.objects.count(),'unread':Notification.objects.filter(user=request.user,seen=False).count()})
@login_required
def incidents(request):return render(request,'monitoring/incidents.html',{'incidents':Incident.objects.select_related('reading').all()[:100]})
@login_required
def incident_detail(request,pk):
 incident=get_object_or_404(Incident,pk=pk)
 return render(request,'monitoring/detail.html',{'incident':incident,'comments':incident.comments.select_related('user'),'events':incident.events.select_related('actor')})
@login_required
def history(request):return render(request,'monitoring/history.html',{'readings':Reading.objects.all()[:200]})
@login_required
def notifications(request):return render(request,'monitoring/notifications.html',{'notifications':Notification.objects.filter(user=request.user).select_related('incident')[:100]})
@login_required
@user_passes_test(lambda u:u.is_staff)
def configuration(request):
 config=current_settings()
 if request.method=='POST':
  try:
   low=float(request.POST['min_temp']);high=float(request.POST['max_temp']);stale=int(request.POST['stale_minutes'])
   if low>=high or stale<1 or stale>10080:raise ValueError()
  except (ValueError,KeyError):return render(request,'monitoring/config.html',{'config':config,'error':'Valeurs invalides : minimum inférieur au maximum, délai entre 1 et 10080.'})
  config.min_temp=low;config.max_temp=high;config.stale_minutes=stale;config.save();return redirect('dashboard')
 return render(request,'monitoring/config.html',{'config':config})
@require_POST
@login_required
def acknowledge(request,pk):
 if not operator(request.user):return HttpResponseForbidden('Opérateur requis')
 incident=get_object_or_404(Incident,pk=pk)
 if incident.status==Incident.OPEN:
  incident.status=Incident.ACK;incident.acknowledged_at=timezone.now();incident.acknowledged_by=request.user;incident.save()
  Event.objects.create(incident=incident,actor=request.user,action='acknowledged')
 return redirect('incident_detail',pk=pk)
@require_POST
@login_required
def resolve(request,pk):
 if not operator(request.user):return HttpResponseForbidden('Opérateur requis')
 incident=get_object_or_404(Incident,pk=pk)
 if incident.status!=Incident.RESOLVED:
  incident.status=Incident.RESOLVED;incident.resolved_at=timezone.now();incident.resolved_by=request.user;incident.save()
  Event.objects.create(incident=incident,actor=request.user,action='resolved')
 return redirect('incident_detail',pk=pk)
@require_POST
@login_required
def comment(request,pk):
 if not operator(request.user):return HttpResponseForbidden('Opérateur requis')
 incident=get_object_or_404(Incident,pk=pk);message=request.POST.get('text','').strip()
 if message and len(message)<=2000:
  Comment.objects.create(incident=incident,user=request.user,text=message)
  Event.objects.create(incident=incident,actor=request.user,action='comment',detail=message[:250])
 return redirect('incident_detail',pk=pk)
@require_POST
@login_required
def mark_seen(request,pk):
 Notification.objects.filter(pk=pk,user=request.user).update(seen=True)
 return redirect('notifications')
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def device_post(request):
    # 1. Validate incoming sensor data
    serializer = ReadingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # 2. Save reading and run existing monitoring logic
    reading = record_measurement(serializer.validated_data)

    # 3. Return API response
    return Response(
        ReadingSerializer(reading).data,
        status=status.HTTP_201_CREATED
    )
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_data(request):return Response({'data':ReadingSerializer(Reading.objects.all()[:200],many=True).data})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_incidents(request):return Response(IncidentSerializer(Incident.objects.all()[:100],many=True).data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_notifications(request):return Response(NotificationSerializer(Notification.objects.filter(user=request.user)[:100],many=True).data)
