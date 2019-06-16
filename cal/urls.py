from django.urls import path
from cal import views

urlpatterns = [
    path('', views.CrearHora.as_view(), name="crear_hora"),
    path('hoy/', views.VerHorasDelDia.as_view(), name="horasdeldia" ),
    path('mañana/', views.VerHorasMañana.as_view(), name="horasmañana"),
    path('calendario/agenda/', views.VerHoras.as_view(), name="horas"),
    path('<int:pk>/', views.DetalleHora.as_view(), name="detallehora"),
    path('<int:pk>/concretar/', views.ConcretarHora.as_view(), name="concretarhora"),
    path('<int:pk>/actualizar/', views.ActualizarHora.as_view(), name="actualizarhora"),
    path('<int:pk>/eliminar/', views.EliminarHora.as_view(), name="eliminarhora"),
    path('<str:pk>/reservar/', views.ReservarHora.as_view(), name="reservarhora"),
]

#Eval
urlpatterns += [
    path('eval/crear/', views.CrearEval.as_view(), name="creareval"),
    path('eval/<int:pk>/', views.DetalleEval.as_view(), name="detalle_eval"),
    path('eval/<int:pk>/eliminar/', views.EliminarEval.as_view(), name="eliminareval"),
    path('eval/<int:pk>/actualizar/', views.ActualizarEval.as_view(), name="actualizareval"),
]

#Autocomplete views
urlpatterns += [
    path('paciente-autocomplete/', views.PacienteAutocomplete.as_view(), name="paciente-autocomplete"),
    path('cotizado/ac/', views.CotizadoAC.as_view(), name="cotizado-ac"),
]

#Calendario

urlpatterns += [
    path('calendario/', views.VistaCalendario.as_view(), name="calendario"),
]
