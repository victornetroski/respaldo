from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
import xml.etree.ElementTree as ET
from sqlalchemy import select
from django.http import JsonResponse
from . import init_db
from .db.models import CFDI
from .models import Documento
from .forms import DocumentoForm
from gestor_asegurados.models import Asegurado
from .processors.xml_processor import CFDIProcessor

@login_required
def lista_documentos(request):
    documentos = Documento.objects.filter(usuario=request.user)
    query = request.GET.get('q')
    if query:
        documentos = documentos.filter(
            Q(nombre_archivo__icontains=query) |
            Q(comentario__icontains(query)) |
            Q(id_asegurado__nombre__icontains(query)) |
            Q(id_poliza__numero_poliza__icontains(query)))
    return render(request, 'gestor_documentos/lista_documentos.html', {
        'documentos': documentos
    })

@login_required
def documentos_asegurado(request, asegurado_id):
    try:
        documentos = Documento.objects.filter(
            id_asegurado_id=asegurado_id,
            usuario=request.user
        ).values(
            'id_documento',
            'tipo_descripcion',
            'nombre_archivo',
            'fecha_subida',
            'datos_xml'
        )
        # Convertir a lista y asegurar que las fechas sean serializables
        documentos_list = list(documentos)
        for doc in documentos_list:
            doc['fecha_subida'] = doc['fecha_subida'].strftime('%Y-%m-%d')
        
        return JsonResponse(documentos_list, safe=False)
    except Exception as e:
        print(f"Error en documentos_asegurado: {str(e)}")  # Para depuración
        return JsonResponse(
            {'error': 'Error al obtener documentos'}, 
            status=500
        )

@login_required
def subir_documento(request):
    initial = {}
    return_to = request.GET.get('return_to')
    asegurado_id = request.GET.get('asegurado')

    if asegurado_id:
        try:
            asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
            initial['id_asegurado'] = asegurado
            if hasattr(asegurado, 'id_poliza'):
                initial['id_poliza'] = asegurado.id_poliza
        except Asegurado.DoesNotExist:
            pass

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                documento = form.save(commit=False)
                documento.usuario = request.user
                
                # Si es XML, verificar si ya existe
                if documento.archivo.name.lower().endswith('.xml'):
                    db_session = init_db()
                    processor = CFDIProcessor(db_session)
                    
                    try:
                        # Guardar temporalmente el archivo para procesarlo
                        archivo_temporal = documento.archivo.read()
                        from io import BytesIO
                        tree = ET.parse(BytesIO(archivo_temporal))
                        
                        root = tree.getroot()
                        # Volver a posicionar el cursor al inicio del archivo
                        documento.archivo.seek(0)
                        
                        uuid = root.find('.//tfd:TimbreFiscalDigital', 
                            {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}).get('UUID')
                        
                        # Resto del proceso XML
                        existing_cfdi = db_session.execute(
                            select(CFDI).where(CFDI.uuid == uuid)
                        ).scalar_one_or_none()
                        
                        if existing_cfdi:
                            docs_existentes = Documento.objects.filter(datos_xml__timbre__UUID=uuid)
                            if docs_existentes.exists():
                                doc_existente = docs_existentes.first()
                                messages.warning(request, 
                                    f'Este XML ya existe en el sistema. ¿Deseas ver los datos del documento existente? '
                                    f'<a href="{reverse("gestor_documentos:ver_xml", args=[doc_existente.id_documento])}">Ver documento</a>')
                                db_session.close()
                                return render(request, 'gestor_documentos/subir_documento.html', {
                                    'form': form,
                                    'documento_existente': doc_existente
                                })
                    except ET.ParseError as xml_error:
                        messages.error(request, f'Error al procesar el XML: El archivo no es un XML válido. {str(xml_error)}')
                        return render(request, 'gestor_documentos/subir_documento.html', {'form': form})
                    finally:
                        db_session.close()
                
                # Asignar asegurado y póliza si fueron seleccionados
                if form.cleaned_data['id_asegurado']:
                    documento.id_asegurado = form.cleaned_data['id_asegurado']
                if form.cleaned_data['id_poliza']:
                    documento.id_poliza = form.cleaned_data['id_poliza']
                
                documento.save()
                messages.success(request, 'Documento guardado exitosamente.')
                
                # Redirigir según el contexto
                if return_to == 'asegurado':
                    return redirect(f'/gestor_asegurados/asegurados/?highlight={asegurado_id}')
                return redirect('gestor_documentos:lista_documentos')
                
            except Exception as e:
                messages.error(request, f'Error al procesar el documento: {str(e)}')
    else:
        form = DocumentoForm(initial=initial)
    
    return render(request, 'gestor_documentos/subir_documento.html', {
        'form': form,
        'return_to': return_to,
        'asegurado_id': asegurado_id
    })

@login_required
def ver_xml(request, id_documento):
    documento = get_object_or_404(Documento, id_documento=id_documento, usuario=request.user)
    
    if not documento.datos_xml:
        return redirect('gestor_documentos:lista_documentos')
    
    return render(request, 'gestor_documentos/ver_xml.html', {
        'documento': documento,
        'datos': documento.datos_xml,
    })

@login_required
def upload_xml_api(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        try:
            archivo = request.FILES['archivo']
            if not archivo.name.lower().endswith('.xml'):
                return JsonResponse({'error': 'El archivo debe ser XML'}, status=400)

            # Obtener el ID del asegurado del POST
            asegurado_id = request.POST.get('asegurado_id')
            asegurado = None
            if asegurado_id:
                try:
                    asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
                except Asegurado.DoesNotExist:
                    return JsonResponse({'error': 'Asegurado no encontrado'}, status=404)

            documento = Documento(
                archivo=archivo,
                nombre_archivo=archivo.name,
                usuario=request.user,
                tipo_descripcion='factura',
                id_asegurado=asegurado
            )
            documento.save()

            return JsonResponse({
                'id_documento': documento.id_documento,
                'nombre': documento.nombre_archivo,
                'datos_xml': documento.datos_xml
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)