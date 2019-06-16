from datetime import datetime, timedelta
from calendar import LocaleHTMLCalendar
from cal.models import Hora, Eval
from collections import Counter, defaultdict
from cal.listas import lista_horas
import pytz

class Diario(object):
    def __init__(self, horas=None, evals=None):
        self.horas = horas
        self.evals = evals
        super(Diario, self).__init__()

    def formathour(self):
        todo = '<caption>Horas agendadas del día</caption>'
        todo += '<thead class="thead-dark"><tr><th scope="col">Hora</th><th scope="col">Duración</th><th scope="col">Paciente</th><th>Prestación</th><th>Médico</th><th>Box</th></tr></thead>'
        cal = ''
        local = pytz.timezone("America/Santiago")
        grupos = defaultdict(list)
        for eva in self.evals:
            grupos[eva.hora.astimezone(local).strftime('%H:%M')].append(eva)
        for reserva in self.horas:
            grupos[reserva.inicio.astimezone(local).strftime('%H:%M')].append(reserva)
        for hora in lista_horas:
            if hora not in grupos:
                grupos[hora] = []
        for x, y in sorted(grupos.items()):
            if len(y) == 0:
                cal += f'<tr class="hora"><td>{x}</td><td></td><td></td><td></td><td></td><td></td></tr>'
            elif len(y) == 1 and y[0] in self.horas:
                cal += f'<tr class="hora reserva" data-href="{y[0].get_absolute_url()}"><td>{x}</td><td>{y[0].duracion}</td><td>{y[0].servicio.presupuesto.paciente.__str__()}</td><td>{y[0].servicio.prestacion.nombre}</td><td>{y[0].medico.get_full_name()}</td><td>{y[0].box}</td></tr>'
            elif len(y) == 1 and y[0] in self.evals:
                cal += f'<tr class="hora reserva" data-href="{y[0].get_absolute_url()}"><td>{x}</td><td>10 minutos</td><td>{y[0].nombre}</td><td>Evaluación</td><td>Mauricio Martínez</td><td>{y[0].box}</td></tr>'
            elif len(y) > 1:
                for z in y:
                    if z is y[0] and z in self.horas:
                        cal += f'<tr class="hora reserva" data-href="{z.get_absolute_url()}"><td>{x}</td><td>{z.duracion}</td><td>{z.servicio.presupuesto.paciente.__str__()}</td><td>{z.servicio.prestacion.nombre}</td><td>{z.medico.get_full_name()}</td><td>{z.box}</td></tr>'
                    elif z is y[0] and z in self.evals:
                        cal += f'<tr class="hora reserva" data-href="{z.get_absolute_url()}"><td>{x}</td><td>10 minutos</td><td>{z.nombre}</td><td>Evaluación</td><td>Mauricio Martínez</td><td>{z.box}</td></tr>'
                    elif z is not y[0] and z in self.horas:
                        cal += f'<tr class="hora reserva" data-href="{z.get_absolute_url()}"><td></td><td>{z.duracion}</td><td>{z.servicio.presupuesto.paciente.__str__()}</td><td>{z.servicio.prestacion.nombre}</td><td>{z.medico.get_full_name()}</td><td>{z.box}</td></tr>'
                    elif z is not y[0] and z in self.evals:
                        cal += f'<tr class="hora reserva" data-href="{z.get_absolute_url()}"><td></td><td>10 minutos</td><td>{z.nombre}</td><td>Evaluación</td><td>Mauricio Martínez</td><td>{z.box}</td></tr>'

        return f'<table class="table table-striped table-hover">{todo}<tbody>{cal}</tbody></table>'

class Calendar(LocaleHTMLCalendar):
    def __init__(self, year=None, month=None, medico=None):
        self.year = year
        self.month = month
        self.medico = medico
        super(Calendar, self).__init__()

    def obtener_agenda(lista):
        return f'agenda/?dia={lista[0].inicio.strftime("%Y-%m-%d")}'

    def formatday(self, day, horas, evals):
        horas_del_dia = horas.filter(inicio__day=day)
        evals_del_dia = evals.filter(hora__day=day)
        d = ''
        for eva in evals_del_dia:
            if self.medico:
                if self.medico.username == "mauriciomartinez":
                    d += '&#128309;'
                else:
                    d+= '&#128308;'
            else:
                d += '&#128308;'
        for hora in horas_del_dia:
            if self.medico:
                if hora.medico == self.medico:
                    d += '&#128309;'
                else:
                    d += '&#128308;'
            else:
                d += '&#128308;'

        if day != 0:
            return f'<td class="dia" data-href="{get_agenda(day, self)}"><span class="date">{day}</span><ul> {d} </ul></td>'
        return '<td></td>'

    def formatweek(self, theweek, horas, evals):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, horas, evals)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        horas = Hora.objects.filter(inicio__year=self.year, inicio__month=self.month)
        evals = Eval.objects.filter(hora__year=self.year, hora__month=self.month)
        cal = f'<table border="0" cellpadding=0 cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, horas, evals)}\n'
        return cal

def get_agenda(day, self):
    return f'agenda/?dia={self.year}-{self.month}-{day}'
