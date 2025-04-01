"""
URL configuration for djangocrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tasks import views as task_views
from gestor_xml import views as gestor_xml_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', task_views.home, name='home'),  # Ruta para la página principal
    path('signup/', task_views.signup, name='signup'),  # Registro de usuario
    path('signin/', task_views.signin, name='signin'),  # Inicio de sesión
    path('logout/', task_views.signout, name='logout'),  # Cerrar sesión
    path('tasks/', include('tasks.urls')),  # Incluye las rutas de `tasks`
    path('gestor_xml/', include('gestor_xml.urls')),  # Incluye las rutas de `gestor_xml`
    path('gestor_asegurados/', include('gestor_asegurados.urls')),  # Incluye las rutas de `gestor_asegurados`
    path('documentos/', include('gestor_documentos.urls', namespace='gestor_documentos')),  # Incluye las rutas de `gestor_documentos`
    path('reembolsos/', include('gestor_reembolsos.urls', namespace='gestor_reembolsos')),  # Incluye las rutas de `gestor_reembolsos`
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
