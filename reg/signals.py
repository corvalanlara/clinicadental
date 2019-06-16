from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from reg.models import Prestacion
import logging

log = logging.getLogger('odo.info')

@receiver(user_logged_in)
def user_logged_in_handler(sender, user, request, **kwargs):
    log.info(f'Usuario {user} se ha conectado')

@receiver(user_logged_out)
def user_logged_out_handler(sender, user, request, **kwargs):
    log.info(f'Usuario {user} se ha desconectado')
