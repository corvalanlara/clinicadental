from cal.models import Hora, Eval
from django import forms
from reg.models import Paciente
from reg.chile import CLRutField
from cal.listas import boxes, medicos, duraciones, lista_horas
from dal import autocomplete
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
import datetime
import pytz

local = pytz.timezone("America/Santiago")

def fuera_del_horario_laboral(hora):
    a = datetime.time(9, 30)
    b = datetime.time(14, 00)
    c = datetime.time(15, 30)
    d = datetime.time(19, 30)
    return not a <= hora.time() <= b and not c <= hora.time() <= d

class ReservarEvalForm(forms.ModelForm):
    class Meta:
        model = Eval
        fields = '__all__'
        widgets = {
            'hora' : forms.DateTimeInput(attrs={'class':'flat'}),
            'box': forms.Select(choices=boxes),
        }
        field_classes = {
            'run' : CLRutField,
        }

    def clean(self):
        cleaned_data = super(ReservarEvalForm, self).clean()
        box = self.cleaned_data.get('box')
        hora = self.cleaned_data.get('hora')
        existe = Eval.objects.filter(box=box).filter(hora=hora)
        trata = Hora.objects.filter(box=box).filter(
            inicio__lt = hora, fin__gt = hora)

        if fuera_del_horario_laboral(hora):
            raise ValidationError(
                _('La hora no está dentro del horario laboral.')
            )

        if hora.astimezone(local).strftime('%H:%M') not in lista_horas:
            raise ValidationError(
                _('La hora de inicio debe ser o en punto o con media hora.')
            )

        if any(existe):
            raise ValidationError(
                _(f'Ya existe una hora de evaluación fijada en ese horario en el box {box}')
            )
        if any(trata):
            raise ValidationError(
                _(f'La hora de evaluación puede comenzar a la misma hora que un tratamiento, pero no durante éste.')
            )

        return cleaned_data

class ConcretarHoraForm(forms.ModelForm):
    class Meta:
        model = Hora
        fields = ('realizada', 'comentarios',)
        widgets = {
            'realizada': forms.HiddenInput(),
        }

class ReservarHoraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReservarHoraForm, self).__init__(*args, **kwargs)
        self.fields['medico'].choices = medicos

    paciente = forms.ModelChoiceField(queryset=Paciente.objects.all(), widget=forms.HiddenInput())
    fin = forms.DurationField(widget=forms.Select(choices=duraciones))
    
    class Meta:
        model = Hora
        fields = ['paciente', 'inicio', 'fin', 'servicio', 'box', 'medico', 'realizada']
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'class':'flat'}),
            'servicio': autocomplete.ModelSelect2(
                url='cotizado-ac',
                forward=['paciente']
            ),
            'realizada': forms.HiddenInput(),
            'box': forms.Select(choices=boxes),
        }
        
    def clean(self):
        self.cleaned_data = super(ReservarHoraForm, self).clean()
        box = self.cleaned_data.get('box')
        inicio = self.cleaned_data.get('inicio')
        duracion = self.cleaned_data.get('fin')
        self.cleaned_data['fin'] = fin = inicio + duracion
        existe = Hora.objects.filter(box=box).filter(
            Q(inicio__lte=inicio, fin__gte=inicio) |
            Q(inicio__lte=fin, fin__gte=fin)
        )

        if fuera_del_horario_laboral(inicio) or fuera_del_horario_laboral(fin):
            raise ValidationError(
                _('La hora no está dentro del horario laboral.')
            )
        
        if inicio.astimezone(local).strftime('%H:%M') not in lista_horas:
            raise ValidationError(
                _('La hora de inicio debe o en punto o con media hora.')
            )

        if any(existe):
            raise ValidationError(
                _(f'Ya existe una hora fijada en ese horario en el box {box}')
            )
        return self.cleaned_data

class ActualizarHoraForm(forms.ModelForm):
    fin = forms.DurationField(widget=forms.Select(choices=duraciones))
    class Meta:
        model = Hora
        fields = ('inicio', 'fin', 'box')
        widgets={
            'inicio': forms.DateTimeInput(attrs={'class':'flat'}),
            'box': forms.Select(choices=boxes),
        }

    def clean(self):
        self.cleaned_data = super(ActualizarHoraForm, self).clean()
        box = self.cleaned_data.get('box')
        inicio = self.cleaned_data.get('inicio')
        duracion = self.cleaned_data.get('fin')
        self.cleaned_data['fin'] = fin = inicio + duracion
        existe = Hora.objects.filter(box=box).filter(
            Q(inicio__lte=inicio, fin__gte=inicio) |
            Q(inicio__lte=fin, fin__gte=fin)
        )
        if fuera_del_horario_laboral(inicio) or fuera_del_horario_laboral(fin):
            raise ValidationError(
                _(f'La hora no está dentro del horario laboral.')
            )
        if inicio.astimezone(local).strftime('%H:%M') not in lista_horas:
            raise ValidationError(
                _('La hora de inicio debe o en punto o con media hora.')
            )
        if any(existe):
            raise ValidationError(
                _(f'Ya existe una hora fijada en ese horario en el box {box}')
            )
        return self.cleaned_data

class HoraForm(ReservarHoraForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        widget=autocomplete.ModelSelect2(url='paciente-autocomplete')
    )
    fin = forms.DurationField(widget=forms.Select(choices=duraciones))

    class Meta:
        model = Hora
        fields = ['paciente', 'servicio', 'inicio', 'fin', 'box', 'medico', 'realizada']
        widgets={
            'servicio': autocomplete.ModelSelect2(
                url='cotizado-ac',
                forward=['paciente']
            ),
            'realizada': forms.HiddenInput(),
            'box': forms.Select(choices=boxes),
            'inicio': forms.DateTimeInput(attrs={'class':'flat'}),
        }
