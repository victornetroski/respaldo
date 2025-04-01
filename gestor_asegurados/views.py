from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Aseguradora, AseguradorasPlan, Poliza, Asegurado, Diagnosticos

# Vistas para Aseguradora
class AseguradoraListView(LoginRequiredMixin, ListView):
    model = Aseguradora
    template_name = 'gestor_asegurados/aseguradora/list.html'
    context_object_name = 'aseguradoras'
    login_url = 'signin'

class AseguradoraCreateView(CreateView):
    model = Aseguradora
    template_name = 'gestor_asegurados/aseguradora/form.html'
    fields = ['id_aseguradora', 'nombre', 'nombre_corto']
    success_url = reverse_lazy('aseguradora-list')

class AseguradoraUpdateView(UpdateView):
    model = Aseguradora
    template_name = 'gestor_asegurados/aseguradora/form.html'
    fields = ['id_aseguradora', 'nombre', 'nombre_corto']
    success_url = reverse_lazy('aseguradora-list')

class AseguradoraDeleteView(DeleteView):
    model = Aseguradora
    template_name = 'gestor_asegurados/aseguradora/confirm_delete.html'
    success_url = reverse_lazy('aseguradora-list')

# Vistas para AseguradorasPlan
class AseguradorasPlanListView(LoginRequiredMixin, ListView):
    model = AseguradorasPlan
    template_name = 'gestor_asegurados/aseguradora_plan/list.html'
    context_object_name = 'planes'
    login_url = 'signin'

class AseguradorasPlanCreateView(LoginRequiredMixin, CreateView):
    model = AseguradorasPlan
    template_name = 'gestor_asegurados/aseguradora_plan/form.html'
    fields = ['id_plan', 'id_aseguradora', 'nombre_plan']
    success_url = reverse_lazy('aseguradoraplan-list')

class AseguradorasPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = AseguradorasPlan
    template_name = 'gestor_asegurados/aseguradora_plan/form.html'
    fields = ['id_plan', 'id_aseguradora', 'nombre_plan']
    success_url = reverse_lazy('aseguradoraplan-list')

class AseguradorasPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = AseguradorasPlan
    template_name = 'gestor_asegurados/aseguradora_plan/confirm_delete.html'
    success_url = reverse_lazy('aseguradoraplan-list')

class PlanCreateView(CreateView):
    model = AseguradorasPlan
    template_name = 'gestor_asegurados/plan_form.html'
    fields = ['nombre_plan', 'id_aseguradora']
    success_url = reverse_lazy('aseguradoraplan-list')  # Actualizado

    def form_valid(self, form):
        messages.success(self.request, 'Plan creado exitosamente.')
        return super().form_valid(form)

class PlanListView(ListView):
    model = AseguradorasPlan
    template_name = 'gestor_asegurados/plan_list.html'
    context_object_name = 'planes'

# Vistas para Póliza
class PolizaListView(LoginRequiredMixin, ListView):
    model = Poliza
    template_name = 'gestor_asegurados/poliza/list.html'
    context_object_name = 'polizas'
    login_url = 'signin'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                Q(id_poliza__icontains=search_query) |
                Q(id_aseguradora__nombre__icontains=search_query) |
                Q(id_plan__nombre_plan__icontains=search_query) |
                Q(numero_poliza__icontains=search_query) |
                Q(fisica_moral__icontains=search_query) |
                Q(nombre__icontains=search_query) |
                Q(apellido_paterno__icontains=search_query) |
                Q(apellido_materno__icontains=search_query) |
                Q(curp__icontains=search_query) |
                Q(rfc__icontains=search_query) |
                Q(calle__icontains=search_query) |
                Q(colonia__icontains=search_query) |
                Q(ciudad_poblacion__icontains=search_query) |
                Q(telefono__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset

class PolizaCreateView(LoginRequiredMixin, CreateView):
    model = Poliza
    template_name = 'gestor_asegurados/poliza/form.html'
    fields = [
        'id_poliza', 'id_aseguradora', 'id_plan', 'numero_poliza',
        'fisica_moral', 'contratante_moral', 'folio_mercantil', 'objeto_social',
        'nombre', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento',
        'lugar_nacimiento', 'curp', 'pais_nacimiento', 'nacionalidad',
        'rfc', 'profesion', 'calle', 'numero_exterior', 'numero_interior',
        'colonia', 'municipio_delegacion', 'entidad_federativa',
        'ciudad_poblacion', 'codigo_postal', 'telefono', 'email',
        'poliza_pdf', 'gobierno', 'cargo', 'dependencia',
        'actua_nombre_propio', 'titular_contratante', 'clabe', 'banco'
    ]
    success_url = reverse_lazy('poliza-list')

class PolizaUpdateView(LoginRequiredMixin, UpdateView):
    model = Poliza
    template_name = 'gestor_asegurados/poliza/form.html'
    fields = [
        'id_poliza', 'id_aseguradora', 'id_plan', 'numero_poliza',
        'fisica_moral', 'contratante_moral', 'folio_mercantil', 'objeto_social',
        'nombre', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento',
        'lugar_nacimiento', 'curp', 'pais_nacimiento', 'nacionalidad',
        'rfc', 'profesion', 'calle', 'numero_exterior', 'numero_interior',
        'colonia', 'municipio_delegacion', 'entidad_federativa',
        'ciudad_poblacion', 'codigo_postal', 'telefono', 'email',
        'poliza_pdf', 'gobierno', 'cargo', 'dependencia',
        'actua_nombre_propio', 'titular_contratante', 'clabe', 'banco'
    ]
    success_url = reverse_lazy('poliza-list')

class PolizaDeleteView(LoginRequiredMixin, DeleteView):
    model = Poliza
    template_name = 'gestor_asegurados/poliza/confirm_delete.html'
    success_url = reverse_lazy('poliza-list')

def poliza_detalle(request, pk):
    try:
        poliza = Poliza.objects.get(id_poliza=pk)  # Ensure `id_poliza` is used if it's the primary key
        data = {
            'id': poliza.id_poliza,
            'aseguradora': poliza.id_aseguradora.nombre,
            'plan': poliza.id_plan.nombre_plan,
            'numero': poliza.numero_poliza,
            'tipo': poliza.fisica_moral,
            'nombre_completo': f"{poliza.nombre} {poliza.apellido_paterno} {poliza.apellido_materno}",
            'curp': poliza.curp,
            'rfc': poliza.rfc,
            'direccion': f"{poliza.calle} {poliza.numero_exterior}, {poliza.colonia}, {poliza.ciudad_poblacion}",
            'telefono': poliza.telefono,
            'email': poliza.email,
        }
        return JsonResponse(data)
    except Poliza.DoesNotExist:
        return JsonResponse({'error': 'Póliza no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

class AseguradoListView(ListView):
    model = Asegurado
    template_name = 'gestor_asegurados/asegurado_list.html'
    context_object_name = 'asegurados'

    def get_queryset(self):
        queryset = Asegurado.objects.select_related('id_poliza').prefetch_related(
            'diagnosticos_relacionados__diagnostico'
        )
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(id_asegurado__icontains=q) |
                Q(nombre__icontains=q) |
                Q(apellido_paterno__icontains=q) |
                Q(apellido_materno__icontains=q) |
                Q(rfc__icontains=q) |
                Q(email__icontains=q) |
                Q(id_poliza__numero_poliza__icontains=q)
            )
        return queryset

class AseguradoCreateView(CreateView):
    model = Asegurado
    fields = '__all__'
    success_url = reverse_lazy('asegurado-list')

class AseguradoUpdateView(UpdateView):
    model = Asegurado
    fields = '__all__'
    success_url = reverse_lazy('asegurado-list')

class AseguradoDeleteView(DeleteView):
    model = Asegurado
    success_url = reverse_lazy('asegurado-list')

def asegurado_detalle(request, pk):
    try:
        asegurado = Asegurado.objects.select_related(
            'id_poliza', 
            'id_poliza__id_aseguradora', 
            'id_poliza__id_plan'
        ).prefetch_related(
            'diagnosticos_relacionados__diagnostico',
            'documento_set'  # Agregamos prefetch para documentos
        ).get(id_asegurado=pk)
        
        # Obtener la póliza del asegurado
        poliza = asegurado.id_poliza
        
        # Modificar la preparación de datos de diagnósticos para manejar mejor las fechas y valores nulos
        diagnosticos_data = []
        for rel in asegurado.diagnosticos_relacionados.all():
            try:
                fecha_inicio = rel.fecha_inicio_padecimiento.strftime('%d/%m/%Y') if rel.fecha_inicio_padecimiento else '-'
                fecha_atencion = rel.fecha_primera_atencion.strftime('%d/%m/%Y') if rel.fecha_primera_atencion else '-'
                
                diagnosticos_data.append({
                    'id': str(rel.diagnostico.id_diagnostico),
                    'diagnostico': rel.diagnostico.diagnostico or '',
                    'fecha_inicio': fecha_inicio,
                    'fecha_primera_atencion': fecha_atencion,
                })
            except AttributeError as e:
                print(f"Error procesando diagnóstico: {str(e)}")
                continue

        # Obtener documentos relacionados
        from gestor_documentos.models import Documento
        documentos = Documento.objects.filter(id_asegurado=asegurado).values(
            'id_documento',
            'tipo_descripcion',
            'nombre_archivo',
            'fecha_subida'
        )
        
        # Convertir fechas a formato string para JSON
        documentos_list = list(documentos)
        for doc in documentos_list:
            doc['fecha_subida'] = doc['fecha_subida'].strftime('%Y-%m-%d')

        data = {
            'id_asegurado': asegurado.id_asegurado,
            'nombre_completo': f"{asegurado.nombre} {asegurado.apellido_paterno} {asegurado.apellido_materno}",
            'fecha_nacimiento': asegurado.fecha_nacimiento.strftime('%d/%m/%Y') if asegurado.fecha_nacimiento else '',
            'genero': asegurado.genero or '',
            'rfc': asegurado.rfc or '',
            'email': asegurado.email or '',
            'telefono': asegurado.telefono or '',
            'tipo_asegurado': asegurado.titular_conyuge_dependiente or '',
            'diagnosticos': diagnosticos_data,
            'poliza': {
                'id_poliza': poliza.id_poliza,
                'numero_poliza': poliza.numero_poliza,
                'aseguradora': poliza.id_aseguradora.nombre,
                'plan': poliza.id_plan.nombre_plan,
                'fisica_moral': poliza.fisica_moral,
                'contratante_moral': poliza.contratante_moral,
                'folio_mercantil': poliza.folio_mercantil,
                'objeto_social': poliza.objeto_social,
                'titular': {
                    'nombre': poliza.nombre,
                    'apellido_paterno': poliza.apellido_paterno,
                    'apellido_materno': poliza.apellido_materno,
                    'fecha_nacimiento': poliza.fecha_nacimiento.strftime('%d/%m/%Y'),
                    'lugar_nacimiento': poliza.lugar_nacimiento,
                    'curp': poliza.curp,
                    'pais_nacimiento': poliza.pais_nacimiento,
                    'nacionalidad': poliza.nacionalidad,
                    'rfc': poliza.rfc,
                    'profesion': poliza.profesion,
                },
                'direccion': {
                    'calle': poliza.calle,
                    'numero_exterior': poliza.numero_exterior,
                    'numero_interior': poliza.numero_interior or '',
                    'colonia': poliza.colonia,
                    'municipio_delegacion': poliza.municipio_delegacion,
                    'entidad_federativa': poliza.entidad_federativa,
                    'ciudad_poblacion': poliza.ciudad_poblacion,
                    'codigo_postal': poliza.codigo_postal,
                },
                'contacto': {
                    'telefono': poliza.telefono,
                    'email': poliza.email,
                },
                'gobierno': {
                    'es_gobierno': poliza.gobierno,
                    'cargo': poliza.cargo,
                    'dependencia': poliza.dependencia,
                },
                'datos_bancarios': {
                    'actua_nombre_propio': poliza.actua_nombre_propio,
                    'titular_contratante': poliza.titular_contratante,
                    'clabe': poliza.clabe,
                    'banco': poliza.banco,
                },
                'tiene_pdf': bool(poliza.poliza_pdf),
                'pdf_url': poliza.poliza_pdf.url if poliza.poliza_pdf else None,
            },
            'documentos': documentos_list  # Agregar documentos a la respuesta
        }
        return JsonResponse(data)
    except Asegurado.DoesNotExist:
        return JsonResponse({'error': 'Asegurado no encontrado'}, status=404)
    except Exception as e:
        print(f"Error en asegurado_detalle: {str(e)}")  # Para depuración
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)

@login_required
def asegurado_list(request):
    asegurados = Asegurado.objects.all()
    highlight_id = request.GET.get('highlight')
    
    return render(request, 'gestor_asegurados/asegurado_list.html', {
        'asegurados': asegurados,
        'highlight_id': highlight_id
    })

@login_required
def get_asegurado_detail(request, asegurado_id):
    try:
        asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
        
        # Obtener diagnósticos relacionados a través de la tabla intermedia
        diagnosticos = [{
            'id': rel.diagnostico.id_diagnostico,
            'diagnostico': rel.diagnostico.diagnostico,
            'fecha_inicio': rel.fecha_inicio_padecimiento.strftime('%d/%m/%Y'),
            'fecha_primera_atencion': rel.fecha_primera_atencion.strftime('%d/%m/%Y')
        } for rel in asegurado.diagnosticos_relacionados.select_related('diagnostico').all()]

        data = {
            'id_asegurado': asegurado.id_asegurado,
            'nombre_completo': f"{asegurado.nombre} {asegurado.apellido_paterno} {asegurado.apellido_materno}",
            'fecha_nacimiento': asegurado.fecha_nacimiento.strftime('%d/%m/%Y'),
            'genero': asegurado.genero,
            'rfc': asegurado.rfc,
            'email': asegurado.email,
            'telefono': asegurado.telefono,
            'tipo_asegurado': asegurado.titular_conyuge_dependiente,
            'diagnosticos': diagnosticos,
        }
        return JsonResponse(data)
    except Asegurado.DoesNotExist:
        return JsonResponse({'error': 'Asegurado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_diagnosticos(request):
    """Vista para obtener los diagnósticos disponibles"""
    query = request.GET.get('q', '')
    asegurado_id = request.GET.get('asegurado_id')
    
    if (asegurado_id):
        # Obtener diagnósticos del asegurado
        asegurado = get_object_or_404(Asegurado, id_asegurado=asegurado_id)
        diagnosticos = asegurado.diagnosticos_relacionados.all().select_related('diagnostico')
        data = []
        for rel in diagnosticos:
            try:
                data.append({
                    'id': rel.diagnostico.id_diagnostico,
                    'diagnostico': rel.diagnostico.diagnostico,  # Cambiado de 'texto' a 'diagnostico'
                    'fecha_inicio': rel.fecha_inicio_padecimiento.strftime('%Y-%m-%d') if rel.fecha_inicio_padecimiento else None,
                    'fecha_primera_atencion': rel.fecha_primera_atencion.strftime('%Y-%m-%d') if rel.fecha_primera_atencion else None
                })
            except AttributeError as e:
                print(f"Error procesando diagnóstico: {str(e)}")
                continue
                
        return JsonResponse(data, safe=False)
    
    # Búsqueda general de diagnósticos
    diagnosticos = Diagnosticos.objects.filter(diagnostico__icontains=query)[:10]
    data = [{'id': d.id_diagnostico, 'diagnostico': d.diagnostico} for d in diagnosticos]  # Cambiado de 'texto' a 'diagnostico'
    return JsonResponse(data, safe=False)

class DiagnosticosListView(LoginRequiredMixin, ListView):
    model = Diagnosticos
    template_name = 'gestor_asegurados/diagnostico/list.html'
    context_object_name = 'diagnosticos'
    login_url = 'signin'

class DiagnosticoCreateView(LoginRequiredMixin, CreateView):
    model = Diagnosticos
    template_name = 'gestor_asegurados/diagnostico/form.html'
    fields = ['diagnostico']
    success_url = reverse_lazy('diagnostico-list')

class DiagnosticoDetailView(DetailView):
    model = Diagnosticos
    template_name = 'gestor_asegurados/diagnostico/detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Diagnosticos, pk=self.kwargs['pk'])