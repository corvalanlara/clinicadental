from reg.models import Paciente, Presupuesto, Prestacion, Ingreso
from django import forms
from reg.chile import CLRutField
from reg.listas import genero_opciones, convenio_opciones, años
from dal import autocomplete
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

class BuscarPacienteForm(forms.Form):
    buscado = forms.CharField(label='Buscar:', strip=True)

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'activo': forms.HiddenInput(),
            'fecha_nacimiento': forms.SelectDateWidget(years=años),
        }
        field_classes = {
            'run': CLRutField,
        }

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['paciente', 'convenio']

    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        widget=autocomplete.ModelSelect2(url='paciente-autocomplete')
    )
    oculto = forms.CharField(widget=forms.HiddenInput, required=False)
    convenio = forms.ChoiceField(choices=convenio_opciones)
    prestaciones = forms.ModelChoiceField(
        queryset=Prestacion.objects.all(),
        widget=autocomplete.ModelSelect2(url='prestacion-ac')
    )
    
    def clean(self):
        cleaned_data = super(PresupuestoForm, self).clean()
        data = self.cleaned_data['oculto']
        if data == "":
            raise ValidationError(_('Se debe ingresar al menos una prestación para generar un presupuesto'))
        return cleaned_data

class PrestacionForm(forms.ModelForm):
    class Meta:
        model = Prestacion
        fields = '__all__'

class FormularioPresupuestario(forms.Form):
    run = CLRutField()
    nombre = forms.CharField(max_length = 100)
    apellido_paterno = nombre = forms.CharField(max_length = 100)
    apellido_materno = nombre = forms.CharField(max_length = 100)
    genero = forms.ChoiceField(choices=genero_opciones)
    fecha_nacimiento = forms.DateField(widget = forms.SelectDateWidget(years=años))
    celular = forms.CharField(max_length = 12, validators=[RegexValidator(regex=r'^\+?569?\d{8}$', message = "Número debe ser ingresado en formato '+569XXXXXXXX'.")])
    correo = forms.EmailField()
    convenio = forms.ChoiceField(choices=convenio_opciones)
    alergias = forms.CharField(max_length = 500, required=False)
    medicamentos = forms.CharField(max_length = 500,required=False)
    oculto = forms.CharField(widget=forms.HiddenInput, required=False)
    prestaciones = forms.ModelChoiceField(
        queryset=Prestacion.objects.all(),
        widget=autocomplete.ModelSelect2(url='prestacion-ac')
    )

    def clean_run(self):
        data = self.cleaned_data['run']
        if Paciente.objects.filter(run=data).exists():
            raise ValidationError(_('Ya existe un paciente con este RUN'))
        return data

    def clean_celular(self):
        data = self.cleaned_data['celular']
        if Paciente.objects.filter(celular=data).exists():
            raise ValidationError(_('Ya existe un paciente con este número telefónico'))
        return data

    def clean_correo(self):
        data = self.cleaned_data['correo']
        if Paciente.objects.filter(correo=data).exists():
            raise ValidationError(_('Ya existe un paciente con este correo-e'))
        return data

    def clean(self):
        cleaned_data = super(FormularioPresupuestario, self).clean()
        data = self.cleaned_data['oculto']
        if data == "":
            raise ValidationError(_('Se debe ingresar al menos una prestación para generar un presupuesto'))
        return cleaned_data

class PagarForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["monto"]
