from django.contrib import admin
from .models import Aseguradora, AseguradorasPlan, Poliza, Asegurado, Diagnosticos, DiagnosticoAsegurado

@admin.register(Aseguradora)
class AseguradoraAdmin(admin.ModelAdmin):
    list_display = ('id_aseguradora', 'nombre', 'nombre_corto')
    search_fields = ('nombre', 'nombre_corto')
    ordering = ('nombre',)

# Registramos los demás modelos
admin.site.register(AseguradorasPlan)
admin.site.register(Poliza)
admin.site.register(Asegurado)
admin.site.register(Diagnosticos)
admin.site.register(DiagnosticoAsegurado)

