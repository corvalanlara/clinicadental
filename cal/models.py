from django.db import models
from django.urls import reverse
from django.conf import settings
import pytz
from babel.dates import format_timedelta
from django.core.validators import RegexValidator

class Eval(models.Model):
    run = models.CharField(max_length = 9, help_text="Sin puntos ni guión")
    nombre = models.CharField(max_length = 200)
    celular_regex = RegexValidator(regex=r'^\+?569?\d{8}$', message = "Número debe ser ingresado en formato '+569XXXXXXXX'.")
    celular = models.CharField("Número de teléfono celular", validators=[celular_regex], max_length = 12, unique = True)
    hora = models.DateTimeField()
    box = models.IntegerField()

    class Meta:
        permissions = (('evaluar', 'Hacer evaluaciones'),)

    def mensaje(self):
        return f'{self.nombre.title()}, recuerda que tienes una evaluación agendada para mañana a las {self.hora.astimezone(pytz.timezone("America/Santiago")).strftime("%H:%M")}'

    def whatsapp(self):
        return self.celular.replace('+', '')
    
    def get_absolute_url(self):
        return reverse('detalle_eval', args=[str(self.id)])

class Hora(models.Model):
    medico = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to = {'groups__name':'Médicos'}, on_delete=models.PROTECT)
    #dia = models.DateField()
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    servicio = models.ForeignKey('reg.Cotizado', on_delete=models.PROTECT)
    box = models.IntegerField()
    realizada = models.BooleanField(default=False)
    comentarios = models.TextField(max_length=1000, blank=True)

    class Meta:
        ordering = ['inicio']

    def ocupado(self, hora, box):
        if self.inicio < hora < self.fin and self.box == box:
            return True
        return False

    @property
    def duracion(self):
        return format_timedelta(self.fin - self.inicio, locale="es_CL")

    def mensaje(self):
        return f'{self.servicio.presupuesto.paciente.nombre.title()}, recuerda que tienes una hora reservada para mañana a las {self.inicio.astimezone(pytz.timezone("America/Santiago")).strftime("%H:%M")} en nuestra clínica dental.'

    @property
    def detalle(self):
        return f'{self.servicio.presupuesto.paciente.__str__()} en box {self.box}'

    def get_absolute_url(self):
        return reverse('detallehora', args=[str(self.id)])
