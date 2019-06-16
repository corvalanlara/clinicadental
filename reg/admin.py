from django.contrib import admin
from reg.models import Paciente, Presupuesto, Prestacion, Ingreso
from django.db import models
from django import forms

admin.site.register(Presupuesto)
admin.site.register(Paciente)
admin.site.register(Prestacion)
admin.site.register(Ingreso)
