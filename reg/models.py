from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
import pytz
import datetime
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from reg.listas import genero_opciones

class Paciente(models.Model):
    run = models.CharField(primary_key = True, max_length = 9, help_text="Sin puntos ni guión")
    nombre = models.CharField(max_length = 100)
    apellido_paterno = models.CharField(max_length = 100)
    apellido_materno = models.CharField(max_length = 100)
    genero = models.CharField(max_length = 2, choices = genero_opciones)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', help_text="e.g. 31/12/1990")
    celular_regex = RegexValidator(regex=r'^\+?569?\d{8}$', message = "Número debe ser ingresado en formato '+569XXXXXXXX'.")
    celular = models.CharField("Número de teléfono celular", validators=[celular_regex], max_length = 12, unique = True)
    correo = models.EmailField(max_length = 200, unique = True, blank = True)
    alergias = models.CharField(max_length=200, blank=True)
    medicamentos = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default = True)

    class Meta:
        ordering = ['apellido_paterno']
        #permissions = (('paciente_management', 'Crear paciente'))

    def __str__(self):
        nombre_completo = f'{self.nombre} {self.apellido_paterno} {self.apellido_materno}'
        return nombre_completo

    def get_absolute_url(self):
        return reverse('detalle_paciente', args=[str(self.run)])

    def whatsapp(self):
        return self.celular.replace('+','')

    @property
    def es_activo(self):
        if self.activo:
            return True
        return False

    @property
    def edad(self):
        hoy = datetime.date.today()
        nacimiento = self.fecha_nacimiento
        return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento,day))

class Prestacion(models.Model):
    nombre = models.CharField(max_length=250)
    monto_default = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Prestaciones"
        ordering = ['nombre']
        
    def __str__(self):
        return self.nombre

class Presupuesto(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    convenio = models.CharField(max_length=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    cotizacion = models.ManyToManyField(Prestacion, through='Cotizado')

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f'{self.paciente} {self.fecha_creacion}'

class Cotizado(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    prestacion = models.ForeignKey(Prestacion, on_delete=models.CASCADE)
    pieza = models.CharField(max_length=2)
    monto = models.IntegerField()

    class Meta:
        ordering = ['presupuesto']

    def __str__(self):
        return f'{self.prestacion} {self.pieza}: {self.monto}'

    def detalle(self):
        if self.pieza:
            return f'{self.prestacion.nombre} en {self.pieza}'
        else:
            return f'{self.prestacion.nombre}'

class Ingreso(models.Model):
    id_pago = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey('Paciente', on_delete=models.PROTECT)
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.IntegerField()

    class Meta:
        ordering = ['fecha_pago']
    
    def get_absolute_url(self):
        return reverse('detalle_paciente', args=[str(self.paciente.run)])
