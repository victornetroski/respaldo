from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from .models import Reembolso, DocumentoReembolso, Reclamacion
from gestor_asegurados.models import Asegurado, Diagnosticos, DiagnosticoAsegurado
from .forms import ReembolsoForm, DiagnosticoReembolsoForm
from .pdf_processor import ReembolsoPDFProcessor
import os
import uuid
from django.db.models import Q
from django.conf import settings

@login_required
def lista_reembolsos(request):
    reembolsos = Reembolso.objects.select_related(
        'asegurado',
        'poliza'
    ).only(
        'id_reembolso',
        'fecha_solicitud',
        'monto_solicitado',
        'estado',
        'asegurado__nombre',
        'asegurado__apellido_paterno',
        'asegurado__apellido_materno',
        'poliza__numero_poliza'
    ).all()
    
    query = request.GET.get('q')
    if query:
        reembolsos = reembolsos.filter(
            Q(id_reembolso__icontains=query) |
            Q(asegurado__nombre__icontains(query)) |
            Q(poliza__numero_poliza__icontains(query)) |
            Q(estado__icontains(query))
        )
    
    return render(request, 'gestor_reembolsos/lista_reembolsos.html', {
        'reembolsos': reembolsos
    })

@login_required
def get_diagnosticos_asegurado(request, asegurado_id):
    """API endpoint para obtener diagnósticos de un asegurado"""
    try:
        asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
        diagnosticos = asegurado.diagnosticos_relacionados.select_related('diagnostico').all()
        
        data = [{
            'id': rel.diagnostico.id_diagnostico,
            'diagnostico': rel.diagnostico.descripcion_diagnostico,
            'fecha_inicio': rel.fecha_inicio_padecimiento.strftime('%d/%m/%Y') if rel.fecha_inicio_padecimiento else None,
            'fecha_atencion': rel.fecha_primera_atencion.strftime('%d/%m/%Y') if rel.fecha_primera_atencion else None,
            'tipo': 'existente'
        } for rel in diagnosticos]
        
        return JsonResponse(data, safe=False)
    except Asegurado.DoesNotExist:
        return JsonResponse([], safe=False)
    except Exception as e:
        print(f"Error en get_diagnosticos_asegurado: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def buscar_diagnosticos(request):
    """API endpoint para buscar diagnósticos existentes"""
    query = request.GET.get('q', '')
    asegurado_id = request.GET.get('asegurado_id')
    
    if query:
        diagnosticos = Diagnosticos.objects.filter(
            Q(descripcion_diagnostico__icontains=query) &
            Q(diagnosticoasegurado__asegurado__id_asegurado=asegurado_id)
        ).distinct()

        resultados = []
        for diag in diagnosticos:
            ultima_relacion = DiagnosticoAsegurado.objects.filter(
                diagnostico=diag,
                asegurado__id_asegurado=asegurado_id
            ).order_by('-fecha_inicio_padecimiento').first()
            
            if ultima_relacion:
                try:
                    # Convertir las fechas al formato deseado
                    fecha_inicio = ultima_relacion.fecha_inicio_padecimiento.strftime('%d/%m/%Y') if ultima_relacion.fecha_inicio_padecimiento else None
                    fecha_atencion = ultima_relacion.fecha_primera_atencion.strftime('%d/%m/%Y') if ultima_relacion.fecha_primera_atencion else None
                    
                    resultados.append({
                        'id_diagnostico': diag.id_diagnostico,
                        'diagnostico': diag.descripcion_diagnostico,
                        'tipo': 'existente',
                        'fecha_inicio_padecimiento': fecha_inicio,
                        'fecha_primera_atencion': fecha_atencion
                    })
                except Exception as e:
                    print(f"Error al formatear fecha: {str(e)}")
                    continue
                    
        return JsonResponse(resultados[:10], safe=False)
    return JsonResponse([], safe=False)

@login_required
def crear_reembolso(request):
    from gestor_asegurados.models import Asegurado, Diagnosticos
    from .forms import ReembolsoForm, DiagnosticoReembolsoForm
    from gestor_documentos.models import Documento
    
    # Capturar parámetros GET para inicialización
    initial_asegurado_id = request.GET.get('asegurado')
    initial_diagnostico_id = request.GET.get('diagnostico')
    initial_diagnostico_texto = request.GET.get('diagnostico_texto')

    # Inicializar formulario de reembolso con el asegurado si se proporciona
    form_initial_data = {}
    if initial_asegurado_id:
        try:
            Asegurado.objects.get(id_asegurado=initial_asegurado_id)
            form_initial_data['asegurado'] = initial_asegurado_id
        except Asegurado.DoesNotExist:
            print(f"Advertencia: Asegurado con ID {initial_asegurado_id} de la URL no encontrado.")
        
    form = ReembolsoForm(initial=form_initial_data)
    
    # Inicializar el formulario de diagnóstico
    diagnostico_form = DiagnosticoReembolsoForm(initial={
        'diagnostico_existente': initial_diagnostico_id,
        'diagnostico_nuevo': initial_diagnostico_texto
    })
    
    # Pasar datos iniciales al contexto para la plantilla
    context = {
        'form': form,
        'diagnostico_form': diagnostico_form,
        'initial_diagnostico_id': initial_diagnostico_id,
        'initial_diagnostico_texto': initial_diagnostico_texto
    }
    return render(request, 'gestor_reembolsos/crear_reembolso.html', context)

@login_required
def detalle_reembolso(request, reembolso_id):
    try:
        reembolso = Reembolso.objects.select_related(
            'asegurado',
            'poliza',
            'usuario_creacion'
        ).prefetch_related(
            'documentos',
            'reclamaciones'
        ).get(id_reembolso=reembolso_id)

        reclamaciones = [{
            'id': rec.id_reclamacion,
            'diagnostico': rec.id_diagnostico.descripcion_diagnostico,
            'es_inicial': not rec.inicial_complementaria,
            'cantidad_partidas': rec.cantidad_partidas,
            'estado': 'Abierta' if rec.abierta else 'Cerrada',
            'fecha_creacion': rec.fecha_creacion.strftime('%d/%m/%Y'),
            'facturas': [{
                'id': fact.documento.id_documento,
                'nombre': fact.documento.nombre_archivo,
                'importe': float(fact.importe),
                'fecha': fact.fecha_asociacion.strftime('%d/%m/%Y'),
            } for fact in rec.facturareclamacion_set.all()],
        } for rec in reembolso.reclamaciones.all()]

        data = {
            'reembolso': {
                'id': reembolso.id_reembolso,
                'fecha_solicitud': reembolso.fecha_solicitud.strftime('%d/%m/%Y'),
                'monto_solicitado': float(reembolso.monto_solicitado),
                'estado': reembolso.get_estado_display(),
                'fecha_actualizacion': reembolso.fecha_actualizacion.strftime('%d/%m/%Y %H:%M'),
                'comentarios': reembolso.comentarios,
            },
            'asegurado': {
                'id': reembolso.asegurado.id_asegurado,
                'nombre_completo': f"{reembolso.asegurado.nombre} {reembolso.asegurado.apellido_paterno} {reembolso.asegurado.apellido_materno}",
                'tipo': reembolso.asegurado.titular_conyuge_dependiente,
            },
            'poliza': {
                'numero': reembolso.poliza.numero_poliza,
                'aseguradora': reembolso.poliza.id_aseguradora.nombre,
                'plan': reembolso.poliza.id_plan.nombre_plan,
            },
            'documentos': [{
                'id': doc.id_documento,
                'tipo': doc.get_tipo_descripcion_display(),
                'nombre': doc.nombre_archivo,
                'fecha': doc.fecha_subida.strftime('%d/%m/%Y'),
            } for doc in reembolso.documentos.all()],
            'reclamaciones': reclamaciones,
            'usuario_creacion': reembolso.usuario_creacion.get_full_name() or reembolso.usuario_creacion.username,
        }
        
        return JsonResponse(data)
    except Reembolso.DoesNotExist:
        return JsonResponse({'error': 'Reembolso no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def editar_reembolso(request, reembolso_id):
    reembolso = get_object_or_404(Reembolso, id_reembolso=reembolso_id)
    if request.method == 'POST':
        pass
    return render(request, 'gestor_reembolsos/editar_reembolso.html', {
        'reembolso': reembolso
    })

@login_required
def reembolsos_asegurado(request, asegurado_id):
    reembolsos = Reembolso.objects.filter(
        asegurado__id_asegurado=asegurado_id
    ).values(
        'id_reembolso',
        'fecha_solicitud',
        'monto_solicitado',
        'estado'
    )
    return JsonResponse(list(reembolsos), safe=False)