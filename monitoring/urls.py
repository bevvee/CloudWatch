from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns=[
 path('',views.dashboard,name='dashboard'),
 path('login/',auth_views.LoginView.as_view(template_name='monitoring/login.html'),name='login'),
 path('logout/',auth_views.LogoutView.as_view(),name='logout'),
 path('history/',views.history,name='history'),
 path('incidents/',views.incidents,name='incidents'),
 path('incidents/<int:pk>/',views.incident_detail,name='incident_detail'),
 path('incidents/<int:pk>/ack/',views.acknowledge,name='acknowledge'),
 path('incidents/<int:pk>/resolve/',views.resolve,name='resolve'),
 path('incidents/<int:pk>/comment/',views.comment,name='comment'),
 path('notifications/',views.notifications,name='notifications'),
 path('notifications/<int:pk>/seen/',views.mark_seen,name='mark_seen'),
 path('configuration/',views.configuration,name='configuration'),
 path('api/post',views.device_post,name='device_post'),
 path('api/data',views.api_data,name='api_data'),
 path('api/incidents',views.api_incidents,name='api_incidents'),
 path('api/notifications',views.api_notifications,name='api_notifications'),
]
