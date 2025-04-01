from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gestor_asegurados/', include('gestor_asegurados.urls')),  # Ensure this line includes the app's URLs
]
