from django.shortcuts import render
from reg.models import Paciente, Presupuesto, Prestacion, Cotizado, Ingreso
from reg.forms import PacienteForm, PresupuestoForm, PrestacionForm, FormularioPresupuestario, PagarForm, BuscarPacienteForm
from django.views.generic.edit import CreateView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, FileResponse, HttpResponse, JsonResponse
from django.urls import reverse
from reg.documento import crear
from dal import autocomplete
from cal.models import Hora, Eval
import datetime
import logging
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
import pytz
from django.contrib.auth.decorators import login_required

log = logging.getLogger('odo.info')

@login_required
def get_precio(request):
    nom = request.GET.get('nom', None)
    data = {
        'precio': Prestacion.objects.get(nombre=nom).monto_default
    }
    return JsonResponse(data)

class CrearPaciente(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Paciente
    template_name = 'reg/paciente_form.html'
    form_class = PacienteForm
    success_message = 'Los datos de %(nombre_completo)s fueron guardados exitosamente.'

    def get_initial(self):
        return {'celular': '+569'}

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            nombre_completo = self.object.__str__(),
        )
   
    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} ha creado al paciente {self.object.__str__()}")
        return response
        
class DetallePaciente(LoginRequiredMixin, DetailView):
    """
    Vista detalle del objeto Paciente.
    """
    model = Paciente
    template_name = 'reg/detalle_paciente.html'

    def get_context_data(self, **kwargs):
        context = super(DetallePaciente, self).get_context_data(**kwargs)
        presupuestos = Presupuesto.objects.filter(paciente__run=self.kwargs.get('pk')).order_by('fecha_creacion')
        cot = {}
        for presupuesto in presupuestos:
            cot[presupuesto] = Cotizado.objects.filter(presupuesto = presupuesto)
        context['presupuestos'] = cot
        realizados = context['realizados'] = Hora.objects.filter(realizada=True).filter(servicio__presupuesto__paciente__run=self.kwargs.get('pk'))
        pagados = context['pagados'] = Ingreso.objects.filter(paciente__pk=self.kwargs.get('pk'))
        context['deuda_total'] = (sum([x.servicio.monto for x in realizados]) - sum([x.monto for x in pagados])) or 0
        context['horas_futuras'] = Hora.objects.filter(servicio__presupuesto__paciente__run=self.kwargs.get('pk')).filter(realizada=False).filter(inicio__gte=datetime.datetime.now(pytz.timezone('America/Santiago')))
        #TODO ingresos realizados
        return context

def index(request):
    """
    Página de inicio
    """
    mañana = datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)
    hoy = datetime.datetime.now(pytz.timezone('America/Santiago'))
    if request.user.groups.filter(name='Administrativos').exists():
        horas = Hora.objects.filter(
            inicio__year = mañana.year,
            inicio__month = mañana.month,
            inicio__day = mañana.day).order_by('inicio')
        evals = Eval.objects.filter(
            hora__year = mañana.year,
            hora__month = mañana.month,
            hora__day = mañana.day).order_by('hora')
    elif request.user.groups.filter(name='Médicos').exists():
        horas = Hora.objects.filter(
            inicio__year = hoy.year,
            inicio__month = hoy.month,
            inicio__day = hoy.day,
            medico = request.user).order_by('inicio')
        evals = Eval.objects.filter(
            hora__year = hoy.year,
            hora__month = hoy.month,
            hora__day = hoy.day).order_by('hora')
    else:
        horas = []
        evals = []

    contexto = {
        'horas': horas,
        'evals': evals,
    }
    return render(request, 'reg/index.html', context=contexto)

@login_required
def CrearPresupuesto(request):
    """
    Crea un presupuesto para un paciente ya inscrito
    """
    if request.method == "POST":
        form = PresupuestoForm(request.POST)
        if form.is_valid():
            presupuesto = Presupuesto()
            presupuesto.paciente = form.cleaned_data['paciente']
            presupuesto.convenio = form.cleaned_data['convenio']
            presupuesto.save()
            #Obtener las prestaciones desde el campo oculto
            prestaciones = form.cleaned_data['oculto']
            prestaciones = prestaciones[:-1]
            prestaciones = prestaciones.split(';')
            prestaciones = [x.split(":") for x in prestaciones]
            cotizaciones = []
            #Crea prestación y cotizado
            for nombre, pieza, monto in prestaciones:
                if not Prestacion.objects.filter(nombre=nombre).exists():
                    servicio = Prestacion()
                    servicio.nombre = nombre
                    servicio.monto_default = monto
                    servicio.save()
                else:
                    servicio = Prestacion.objects.get(nombre=nombre)
                cotizado = Cotizado()
                cotizado.presupuesto = presupuesto
                cotizado.prestacion = servicio
                cotizado.pieza = pieza
                cotizado.monto = int(monto)
                cotizado.save()
                cotizaciones.append(cotizado)
            pdf = crear(presupuesto.paciente, presupuesto, cotizaciones)
            response = HttpResponse(content_type='application/docx')
            response['Content-Disposition'] = 'attachment; filename="hola.docx"'
            response.write(pdf)
            log.info(f'Usuario {request.user} ha creado el presupuesto n° {presupuesto.id} para un nuevo paciente: {presupuesto.paciente.__str__()}')
            messages.success(request, f'Has creado exitosamente un presupuesto para {presupuesto.paciente.__str__()}')
            return response
    else:
        form = PresupuestoForm()
    
    contexto = {'form': form}
    return render(request, 'reg/presupuesto_form.html', contexto)

class CrearPrestacion(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Prestacion
    template_name = 'reg/prestacion_form.html'
    form_class = PrestacionForm
    success_message = 'Se ha creado la prestación %(nombre)s con monto base de %(monto_default)s'
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} ha creado la prestación {self.object.nombre} con un monto de {self.object.monto_default}")
        return response

@login_required
def presupuesto(request):
    """
    Vista para formulario único que crea un Paciente y un Presupuesto nuevo.
    """
    if request.method == 'POST':
        form = FormularioPresupuestario(request.POST)
        if form.is_valid():
            #Crear nuevo paciente
            paciente = Paciente()
            paciente.run = form.cleaned_data['run']
            paciente.nombre = form.cleaned_data['nombre'].title()
            paciente.apellido_paterno = form.cleaned_data['apellido_paterno'].title()
            paciente.apellido_materno = form.cleaned_data['apellido_materno'].title()
            paciente.genero = form.cleaned_data['genero']
            paciente.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            paciente.celular = form.cleaned_data['celular']
            paciente.correo = form.cleaned_data['correo']
            paciente.alergias = form.cleaned_data['alergias']
            paciente.medicamentos = form.cleaned_data['medicamentos']
            paciente.activo = True
            paciente.save()
            #Crear nuevo Presupuesto
            presupuesto = Presupuesto()
            presupuesto.paciente = paciente
            presupuesto.convenio = form.cleaned_data['convenio']
            presupuesto.save()
            #Obtener las prestaciones desde el campo oculto
            prestaciones = form.cleaned_data['oculto']
            prestaciones = prestaciones[:-1]
            prestaciones = prestaciones.split(';')
            prestaciones = [x.split(":") for x in prestaciones]
            cotizaciones = []
            #Crea prestación y cotizado
            for nombre, pieza, monto in prestaciones:
                if not Prestacion.objects.filter(nombre=nombre).exists():
                    servicio = Prestacion()
                    servicio.nombre = nombre
                    servicio.monto_default = monto
                    servicio.save()
                else:
                    servicio = Prestacion.objects.get(nombre=nombre)
                cotizado = Cotizado()
                cotizado.presupuesto = presupuesto
                cotizado.prestacion = servicio
                cotizado.pieza = pieza
                cotizado.monto = int(monto)
                cotizado.save()
                cotizaciones.append(cotizado)
            pdf = crear(paciente, presupuesto, cotizaciones)
            response = HttpResponse(content_type='application/docx')
            response['Content-Disposition'] = 'attachment; filename="hola.docx"'
            response.write(pdf)
            log.info(f'Usuario {request.user} ha creado el presupuesto n° {presupuesto.id} para un nuevo paciente: {paciente.__str__()}')
            messages.success(request, f'Has creado exitosamente un presupuesto para {paciente.__str__()}')
            return response
    else:
        form = FormularioPresupuestario(
            initial = {
                'celular':'+569'
            }
        )
    
    contexto = {'form': form}
    return render(request, 'reg/formulario_total.html', contexto)

class PrestacionAC(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        todos = Prestacion.objects.all()
        if self.q:
            todos = todos.filter(nombre__istartswith=self.q)
        return todos

class IngresoPago(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ingreso
    template_name = 'reg/ingreso_form.html'
    form_class = PagarForm
    success_message = 'Se ha registrado el pago realizado por %(nombre_completo)s con monto base de %(monto)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            nombre_completo = self.object.paciente.__str__(),
            monto = self.object.monto,
        )

    def get_context_data(self, **kwargs):
        context = super(IngresoPago, self).get_context_data(**kwargs)
        context['realizados'] = Hora.objects.filter(realizada=True).filter(
            servicio__presupuesto__paciente__run=self.kwargs.get('pk'))
        return context
    
    def form_valid(self, form):
        ingreso = form.save(commit=False)
        ingreso.paciente = Paciente.objects.get(run=self.kwargs['pk'])
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} ha registrado un ingreso (id: {self.object.id_pago}) realizado por {self.object.paciente.__str__()} por un monto de {self.object.monto}")
        return response
