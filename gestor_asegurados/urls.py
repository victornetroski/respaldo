from django.urls import path
from .views import *
from . import views
from .views import AseguradoListView, AseguradoCreateView, AseguradoUpdateView, AseguradoDeleteView, DiagnosticosListView, DiagnosticoCreateView, DiagnosticoDetailView

urlpatterns = [
    path('aseguradoras/', AseguradoraListView.as_view(), name='aseguradora-list'),
    
    # URLs para AseguradorasPlan
    path('planes/', PlanListView.as_view(), name='aseguradoraplan-list'),  # Cambiado de lista_planes
    path('planes/crear/', PlanCreateView.as_view(), name='aseguradoraplan-create'),  # Cambiado de crear_plan
    path('planes/<str:pk>/editar/', AseguradorasPlanUpdateView.as_view(), name='aseguradoraplan-update'),
    path('planes/<str:pk>/eliminar/', AseguradorasPlanDeleteView.as_view(), name='aseguradoraplan-delete'),

    # URLs para Polizas - Updated to handle string IDs
    path('polizas/', PolizaListView.as_view(), name='poliza-list'),
    path('polizas/crear/', PolizaCreateView.as_view(), name='poliza-create'),
    path('polizas/<str:pk>/editar/', PolizaUpdateView.as_view(), name='poliza-update'),  # Changed from int:pk to str:pk
    path('polizas/<str:pk>/eliminar/', PolizaDeleteView.as_view(), name='poliza-delete'),  # Changed from int:pk to str:pk
    path('polizas/<str:pk>/detalle/', views.poliza_detalle, name='poliza-detalle'),
    
    # URLs para Asegurados
    path('asegurados/', AseguradoListView.as_view(), name='asegurado-list'),
    path('asegurados/crear/', AseguradoCreateView.as_view(), name='asegurado-create'),
    path('asegurados/<str:pk>/editar/', AseguradoUpdateView.as_view(), name='asegurado-update'),
    path('asegurados/<str:pk>/eliminar/', AseguradoDeleteView.as_view(), name='asegurado-delete'),
    path('asegurados/<str:pk>/detalle/', views.asegurado_detalle, name='asegurado-detalle'),

    path('api/diagnosticos/', views.get_diagnosticos, name='get_diagnosticos'),

    path('diagnostico/', views.DiagnosticosListView.as_view(), name='diagnostico-list'),
    path('diagnostico/create/', views.DiagnosticoCreateView.as_view(), name='diagnostico_create'),
    path('diagnostico/<pk>/', views.DiagnosticoDetailView.as_view(), name='diagnostico_detail'),

]