from django.apps import AppConfig
from watson import search as watson

class RegConfig(AppConfig):
    name = 'reg'
    def ready(self):
        Paciente = self.get_model("Paciente")
        watson.register(Paciente, fields=('run','nombre','apellido_paterno','apellido_materno'))
        from reg.signals import user_logged_in_handler
        from reg.signals import user_logged_out_handler
