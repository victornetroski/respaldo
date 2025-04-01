from django.urls import path
from . import views

app_name = 'gestor_reembolsos'

urlpatterns = [
    path('', views.lista_reembolsos, name='lista_reembolsos'),
    path('nuevo/', views.crear_reembolso, name='crear_reembolso'),
    path('<int:reembolso_id>/', views.detalle_reembolso, name='detalle_reembolso'),
    path('<int:reembolso_id>/editar/', views.editar_reembolso, name='editar_reembolso'),
    path('asegurado/<str:asegurado_id>/', views.reembolsos_asegurado, name='reembolsos_asegurado'),
    path('diagnosticos/<str:asegurado_id>/', views.get_diagnosticos_asegurado, name='diagnosticos_asegurado'),
    path('api/buscar-diagnosticos/', views.buscar_diagnosticos, name='buscar_diagnosticos'),
]
