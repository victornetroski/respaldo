from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import  XMLUploadForm
from .models import XMLFile
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import xml.etree.ElementTree as ET  # Para procesar XML
from reportlab.pdfgen import canvas  # Para generar PDFs
import logging
from xml.etree.ElementTree import ParseError
import os
from PyPDF2 import PdfReader, PdfWriter
from django.conf import settings

logger = logging.getLogger(__name__)

# Create your views here.
def procesar_xml(file):
    try:
        # Intentar cargar y analizar el archivo XML
        tree = ET.parse(file)  # Esto carga el archivo XML en un árbol
        root = tree.getroot()  # Obtiene la raíz del árbol

        print("Estructura del XML:", ET.tostring(root, encoding='utf-8').decode('utf-8'))

        # Si llega aquí, el XML se cargó correctamente
        print("XML cargado correctamente.")

        # Declarar el namespace necesario (para manejar `tfd`)
        namespaces = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}

        # Buscar el nodo <tfd:TimbreFiscalDigital>
        timbre = root.find('.//tfd:TimbreFiscalDigital', namespaces)
        if timbre is not None:
            uuid = timbre.attrib.get('UUID', None)  # Extraer el valor de `UUID`
            if uuid:
                print(f"Valor de UUID extraído: {uuid}")
            else:
                print("No se encontró el atributo UUID.")
        else:
            print("No se encontró el nodo <tfd:TimbreFiscalDigital>.")

        return root
    except ET.ParseError as e:
        # Capturar errores relacionados con el formato del XML
        print(f"Error en el formato del XML: {e}")
        return None
    except Exception as e:
        # Capturar otros errores genéricos
        print(f"Error inesperado: {e}")
        return None

        
def extract_ns0_elements(root):
    # Inicializar un diccionario para almacenar etiquetas y atributos
    ns0_data = []

    # Definir el espacio de nombres (ajustar según el XML)
    namespaces = {'ns0': 'http://www.sat.gob.mx/cfd/4'}

    # Recorrer todos los nodos con el prefijo 'ns0:'
    for elem in root.iter():
        if elem.tag.startswith("{http://www.sat.gob.mx/cfd/4}"):
            # Obtener la etiqueta sin el espacio de nombres
            tag_name = elem.tag.split('}', 1)[1]
            # Obtener sus atributos
            ns0_data.append({tag_name: elem.attrib})

    return ns0_data



def extract_total(ns0_data):
    # Recorrer los datos y buscar el atributo 'Total' en la etiqueta 'Comprobante'
    for data in ns0_data:
        if 'Comprobante' in data:  # Verificar si el nodo es 'Comprobante'
            return data['Comprobante'].get('Total')  # Devolver el valor de 'Total'
    return None  # Retornar None si no se encuentra el atributo


def fill_pdf_template(pdf_template_path, response, total_value):
    # Leer el PDF editable
    reader = PdfReader(pdf_template_path)
    writer = PdfWriter()

    # Listar todos los campos del formulario para depuración
    fields = reader.get_fields()
    print("Campos disponibles en el formulario:", fields.keys())

    # Copiar páginas y rellenar el campo Total
    for page in reader.pages:
        writer.add_page(page)

    # Rellenar el campo 'Total' (ajustar según nombre del campo)
    writer.update_page_form_field_values(
        writer.pages[1],
        {"Text Field 599": total_value}  # Aquí se llena el valor de Total
    )

    # Guardar el resultado directamente en la respuesta HTTP
    writer.write(response)



@login_required
def upload_xml(request):
    if request.method == 'POST':
        try:
            form = XMLUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']

                # Validar si el archivo no está vacío
                if file.size == 0:
                    return HttpResponse("El archivo está vacío. Por favor, sube un archivo XML válido.", status=400)

                # Procesar el archivo XML
                root = procesar_xml(file)

                # Extraer todos los elementos relacionados con 'ns0'
                ns0_data = extract_ns0_elements(root)

                """# Depurar en consola
                print("Datos extraídos con prefijo 'ns0':", ns0_data)"""

                # Obtener el valor de 'Total' en la etiqueta 'Comprobante'
                total = extract_total(ns0_data)
                print("Valor extraído para 'Total':", total) 

                # Ruta al archivo de plantilla desde la carpeta del proyecto
                pdf_template_path = os.path.join(settings.BASE_DIR, 'tasks', 'pdfs', 'BUPA_FORMATO_REEMBOLSO.pdf')

                # Crear el response para el PDF
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="output.pdf"'

                # Rellenar el PDF con el valor de 'Total'
                fill_pdf_template(pdf_template_path, response, total)

                return response  # Retornar el PDF generado
        except Exception as e:
            logger.error(f"Error durante el procesamiento: {e}")
            return HttpResponse("Error en el servidor.", status=500)
    else:
        form = XMLUploadForm()

    return render(request, 'upload_xml.html', {'form': form})

