from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
class Command(BaseCommand):
 help='Crée le groupe Operateurs (ajoutez ensuite trois utilisateurs depuis /admin/)'
 def handle(self,*args,**kwargs):
  group,_=Group.objects.get_or_create(name='Operateurs')
  self.stdout.write(self.style.SUCCESS('Groupe Operateurs prêt. Assignez 3 utilisateurs actifs dans Django admin.'))
