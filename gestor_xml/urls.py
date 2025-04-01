from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_xml, name='upload_xml'),  # Página principal del gestor xml
    path('upload_xml/', views.upload_xml, name='upload_xml'),
]
