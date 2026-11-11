from django.test import TestCase
from django.contrib.auth.models import User,Group
from unittest.mock import patch
from .models import Reading,Incident,Notification,Event
class DeviceTests(TestCase):
 @patch('monitoring.ntfy_service.requests.post')
 def test_public_ingestion_and_incident(self, post):
  post.return_value.raise_for_status.return_value=None
  group=Group.objects.create(name='Operateurs')
  for i in range(3):User.objects.create_user(username=f'op{i}',password='test-pass-123').groups.add(group)
  self.assertEqual(self.client.post('/api/post',{'temp':12,'hum':55},content_type='application/json').status_code,201)
  self.assertEqual(Incident.objects.count(),1)
  self.assertEqual(Notification.objects.count(),3)
  self.assertEqual(self.client.post('/api/post',{'temp':13,'hum':50},content_type='application/json').status_code,201)
  self.assertEqual(Incident.objects.count(),1)
  self.assertEqual(Reading.objects.count(),2)
  self.assertEqual(post.call_count,1)
  self.assertEqual(post.call_args.kwargs['json'],{'temp':12.0,'hum':55.0,'message':'Critical temperature!'})

 def test_invalid_payload_rejected(self):
  response=self.client.post('/api/post',{'temp':150,'hum':50},content_type='application/json')
  self.assertEqual(response.status_code,400)
  self.assertEqual(Reading.objects.count(),0)
