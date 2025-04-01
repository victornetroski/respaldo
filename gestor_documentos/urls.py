from django.urls import path
from . import views

app_name = 'gestor_documentos'

urlpatterns = [
    path('', views.lista_documentos, name='lista_documentos'),
    path('subir/', views.subir_documento, name='subir_documento'),
    path('ver/<str:id_documento>/', views.ver_xml, name='ver_xml'),
    path('api/asegurado/<int:asegurado_id>/', views.documentos_asegurado, name='documentos_asegurado'),
    path('api/upload-xml/', views.upload_xml_api, name='upload_xml_api'),
]
