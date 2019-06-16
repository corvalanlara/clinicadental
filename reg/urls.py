from django.urls import path
from reg import views
from reg.models import Prestacion

urlpatterns = [
    path('', views.index, name="inicio"),
    path('paciente/nuevo/', views.CrearPaciente.as_view(), name="crear_paciente"),
    path('paciente/<str:pk>/', views.DetallePaciente.as_view(), name="detalle_paciente"),
    path('paciente/<str:pk>/pagar/', views.IngresoPago.as_view(), name="ingresar_pago"),
    path('prestacion/nuevo/', views.CrearPrestacion.as_view(), name="crear_prestacion"),
    path('presupuesto/nuevo/', views.CrearPresupuesto, name="crear_presupuesto"),
    path('nuevo/', views.presupuesto, name="crear_formtotal"),
]

urlpatterns += [
    path('prestacion/ac/', views.PrestacionAC.as_view(create_field='nombre'), name="prestacion-ac"),
]

urlpatterns += [
    path('nuevo/ajax/chequear/', views.get_precio, name="get_precio"),
]
