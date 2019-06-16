from django.contrib.auth.models import User
from datetime import timedelta

boxes = [(x, x) for x in range(1, 4)]
medicos = [(x.pk, x.get_full_name()) for x in User.objects.filter(groups__name='Médicos')]
duraciones = [
    (timedelta(0, 1800), '30 minutos'),
    (timedelta(0, 3600), '1 hora'),
]
lista_horas = ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00']
