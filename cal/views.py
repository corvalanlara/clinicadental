from django.shortcuts import render
from cal.models import Hora, Eval
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from dal import autocomplete
from reg.models import Paciente, Cotizado
from cal.forms import HoraForm, ConcretarHoraForm, ActualizarHoraForm, ReservarHoraForm, ReservarEvalForm
from django.db.models import Q
import datetime
import calendar
from cal.calendario import Calendar, Diario
from django.utils.safestring import mark_safe
import logging
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
import pytz
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

log = logging.getLogger('odo.info')

class VerHorasMañana(LoginRequiredMixin, ListView):
    model = Hora
    template_name = 'cal/agenda.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cal = Diario(horas = Hora.objects.filter(
            inicio__year = (datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)).year,
            inicio__month = (datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)).month,
            inicio__day = (datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)).day,
        ).order_by('inicio'), evals = Eval.objects.filter(
            hora__year = (datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)).year,
            hora__month = (datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)).month,
            hora__day = (datetime.datetime.now(pytz.timezone('America/Santiago')) - datetime.timedelta(-1)).day,
        ).order_by('hora'))
        html_cal = cal.formathour()
        context['agenda'] = mark_safe(html_cal)
        return context

class VerHorasDelDia(LoginRequiredMixin, ListView):
    model = Hora
    template_name = 'cal/agenda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cal = Diario(horas = Hora.objects.filter(
            inicio__year = datetime.datetime.now(pytz.timezone('America/Santiago')).year,
            inicio__month = datetime.datetime.now(pytz.timezone('America/Santiago')).month,
            inicio__day = datetime.datetime.now(pytz.timezone('America/Santiago')).day,
        ).order_by('inicio'), evals = Eval.objects.filter(
            hora__year = datetime.datetime.now(pytz.timezone('America/Santiago')).year,
            hora__month = datetime.datetime.now(pytz.timezone('America/Santiago')).month,
            hora__day = datetime.datetime.now(pytz.timezone('America/Santiago')).day, 
        ).order_by('hora'))
        html_cal = cal.formathour()
        context['agenda'] = mark_safe(html_cal)
        return context

class VerHoras(LoginRequiredMixin, ListView):
    model = Hora
    template_name = 'cal/agenda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dia = self.request.GET.get('dia', None)
        year, month, day = dia.split('-')
        cal = Diario(horas = Hora.objects.filter(
            inicio__year = year,
            inicio__month = month,
            inicio__day = day,
        ).order_by('inicio'), evals = Eval.objects.filter(
            hora__year = year,
            hora__month = month,
            hora__day = day,
        ).order_by('hora'))
        html_cal = cal.formathour()
        context['agenda'] = mark_safe(html_cal)
        return context

class CrearEval(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Eval
    template_name = 'cal/eval_form.html'
    form_class = ReservarEvalForm
    success_message = 'Has reservado con éxito una evaluación para %(nombre)s'

    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} reservó la hora n° {self.object.pk} para {self.object.nombre}")
        return response

class DetalleEval(LoginRequiredMixin, DetailView):
    model = Eval
    template_name = 'cal/detalle_eval.html'
    context_object_name = 'eval'

class ActualizarEval(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Eval
    template_name = 'cal/actualizar_eval.html'
    form_class = ReservarEvalForm
    success_message = 'Has actualizado exitosamente la evaluación n° %(ide)s asignada a %(nombre)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ide = self.object.pk,
            nombre = self.object.nombre,
        )


    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} realizó una actualización a la hora {self.object.pk}")
        return response

class EliminarEval(LoginRequiredMixin, DeleteView):
    model = Eval
    success_url = reverse_lazy('inicio')
    template_name = 'cal/eliminar_eval.html'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log.info(f"Usuario {self.request.user} ha eliminado la hora n° {obj.pk} reservada para {obj.nombre}")
        messages.success(request, f'Has eliminado exitosamente la hora reservada para {obj.nombre}')
        return super().delete(request, *args, **kwargs)

class CrearHora(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Hora
    template_name = 'cal/hora_form.html'
    form_class = HoraForm
    success_message = 'Has reservado exitosamente una hora para %(nombre_completo)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            nombre_completo = self.object.servicio.presupuesto.paciente.__str__(),
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} reservó la hora n° {self.object.id} para el paciente {self.object.servicio.presupuesto.paciente.__str__()}")
        return response

class ActualizarHora(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Hora
    template_name = 'cal/actualizar_hora.html'
    form_class = ActualizarHoraForm
    success_message = 'Has actualizado exitosamente la hora n° %(ide)s asignada a %(paciente)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ide = self.object.id,
            paciente = self.object.servicio.presupuesto.paciente.__str__(),
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} realizó una actualización a la hora {self.object.id}")
        return response

class EliminarHora(LoginRequiredMixin, DeleteView):
    model = Hora
    success_url = reverse_lazy('inicio')
    template_name = 'cal/eliminar_hora.html'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log.info(f"Usuario {self.request.user} ha eliminado la hora n° {obj.id} reservada para {obj.servicio.presupuesto.paciente.__str__()}")
        messages.success(request, f'Has eliminado exitosamente la hora reservada para {obj.servicio.presupuesto.paciente.__str__()}')
        return super().delete(request, *args, **kwargs)

class DetalleHora(LoginRequiredMixin, DetailView):
    model = Hora
    template_name = 'cal/detalle_hora.html'
    context_object_name = 'hora'

class ReservarHora(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Hora
    template_name = 'cal/hora_form.html'
    form_class = ReservarHoraForm
    success_message = 'Has reservado exitosamente una hora para %(nombre_completo)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            nombre_completo = self.object.servicio.presupuesto.paciente.__str__(),
        )

    def get_initial(self):
        super(ReservarHora, self).get_initial()
        paciente = get_object_or_404(Paciente, pk=self.kwargs['pk'])
        return {'paciente': paciente}

    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f'Usuario {self.request.user} ha reservado una hora para {self.object.servicio.presupuesto.paciente.__str__()}')
        return response

class ConcretarHora(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Hora
    template_name = 'cal/concretar_hora.html'
    form_class = ConcretarHoraForm
    success_message = 'Has asignado exitosamente el cobro por el servicio entregado a %(paciente)s'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            paciente = self.object.servicio.presupuesto.paciente.__str__(),
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        log.info(f"Usuario {self.request.user} asignó un cobro por el servicio entregado (según la hora n° {self.object.id}) al paciente {self.object.servicio.presupuesto.paciente.__str__()}")
        return response

    def get_success_url(self):
        return reverse_lazy('detalle_paciente', kwargs={'pk': self.object.servicio.presupuesto.paciente.pk})

    def get(self, request, *args, **kwargs):
        hora = Hora.objects.get(pk=kwargs['pk'])
        realizada = hora.realizada
        form = self.form_class(
            initial = {
                'realizada': not realizada,
            }
        )
        return render(request, self.template_name, {'form': form, 'hora': hora})

class PacienteAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        todos = Paciente.objects.all()
        if self.q:
            todos = todos.filter(
                Q(nombre__istartswith=self.q) | Q(apellido_paterno__istartswith=self.q)
                    )
        return todos

class CotizadoAC(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        todos = Cotizado.objects.select_related()
        paciente = self.forwarded.get('paciente', None)
        if paciente:
            #Entrega los servicios cotizados que no han sido agendados
            #(i.e. asociados a una Hora) aunque no se hayan realizado aún.
            todos = todos.filter(presupuesto__paciente=paciente).exclude(hora__servicio__presupuesto__paciente=paciente)
        if self.q:
            todos = todos.filter(prestacion__nombre__istartswith=self.q)
        return todos

class VistaCalendario(LoginRequiredMixin, ListView):
    model = Hora
    template_name = 'cal/calendario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('mes', None))
        cal = Calendar(d.year, d.month, self.request.user)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['mes_previo'] = mes_previo(d)
        context['mes_siguiente'] = mes_siguiente(d)
        return context

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.datetime.now(pytz.timezone('America/Santiago'))

def mes_previo(d):
    primero = d.replace(day=1)
    mes_anterior = primero - datetime.timedelta(days=1)
    mes = 'mes='+ str(mes_anterior.year) + '-' + str(mes_anterior.month)
    return mes

def mes_siguiente(d):
    dias_en_el_mes = calendar.monthrange(d.year, d.month)[1]
    ultimo = d.replace(day=dias_en_el_mes)
    mes_siguiente = ultimo + datetime.timedelta(days=1)
    mes = 'mes=' + str(mes_siguiente.year) + '-' + str(mes_siguiente.month)
    return mes
