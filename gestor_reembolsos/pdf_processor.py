import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from PyPDF2.generic import NameObject, createStringObject

class ReembolsoPDFProcessor:
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'templates_pdf',
            'reembolsos',
            'BUPA_FORMATO_REEMBOLSO.pdf'
        )

    def generate_reembolso_pdf(self, reembolso, output_path):
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Leer la plantilla
            reader = PdfReader(self.template_path)
            writer = PdfWriter()
            
            # Agregar todas las páginas de la plantilla
            for page in reader.pages:
                writer.add_page(page)

            # Preparar los campos para cada página
            nombre_completo = f"{reembolso.asegurado.nombre} {reembolso.asegurado.apellido_paterno} {reembolso.asegurado.apellido_materno}"
            print(f"Intentando escribir nombre: {nombre_completo}")  # Debug

            page_fields = {
                0: {  # Primera página
                    "Text Field 378": nombre_completo,
                    "Text Field 379": reembolso.poliza.numero_poliza,
                    "Text Field 487": reembolso.asegurado.rfc,
                    "Text Field 404": reembolso.poliza.calle,
                    "Text Field 405": reembolso.poliza.numero_exterior,
                    "Text Field 406": reembolso.poliza.numero_interior,
                    "Text Field 407": reembolso.poliza.colonia,
                    "Text Field 408": reembolso.poliza.municipio_delegacion,
                    "Text Field 409": reembolso.poliza.entidad_federativa,
                    "Text Field 4010": reembolso.poliza.entidad_federativa,
                    "Text Field 4011": reembolso.poliza.codigo_postal,
                },
                1: {  # Segunda página
                    "Text Field 599": str(reembolso.monto_solicitado),
                    
                }
            }

            """# Antes de actualizar, mostrar los campos disponibles
            print("Campos disponibles en el PDF:")
            fields = reader.get_fields()
            for key in fields.keys():
                print(f"Campo encontrado: {key}")"""

            # Actualizar campos específicos por página
            for page_num in range(len(writer.pages)):
                if page_num in page_fields:
                    print(f"Actualizando campos en página {page_num}:")  # Debug
                    print(page_fields[page_num])  # Debug
                    writer.update_page_form_field_values(
                        writer.pages[page_num],
                        page_fields[page_num]
                    )
            
            # Guardar el PDF
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            return output_path
        except Exception as e:
            print(f"Error generando PDF: {str(e)}")
            raise

    def _draw_field(self, canvas, field_name, value, x, y):
        canvas.drawString(x, y, str(value))

    """def _get_field_names(self, pdf_path):
        #Método de ayuda para obtener los nombres de los campos del PDF
        reader = PdfReader(pdf_path)
        fields = reader.get_fields()
        for key in fields.keys():
            print(f"Campo encontrado: {key}")
        return fields"""