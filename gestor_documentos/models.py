from django.db import models
from django.contrib.auth.models import User  # Para relacionar con el usuario que sube el documento
from django.core.exceptions import ValidationError
from gestor_asegurados.models import Asegurado, Poliza  # Relación con asegurados y pólizas
import os  # Para identificar el tipo de documento automáticamente
import uuid
import datetime

def formato_tamaño(bytes):
    """Convierte bytes a formato legible (KB, MB, GB)"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

def generar_id_documento():
    """Genera un ID único alfanumérico con prefijo y fecha"""
    fecha = datetime.datetime.now().strftime("%Y%m%d")
    uuid_corto = str(uuid.uuid4())[:8]
    return f"DOC-{fecha}-{uuid_corto}"

class Documento(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('desglose', 'Desglose'),
        ('endoso', 'Endoso'),
        ('estado_cuenta', 'Estado de Cuenta'),
        ('factura', 'Factura'),
        ('formato_reembolso', 'Formato de Reembolso'),
        ('id_oficial', 'ID Oficial'),
        ('informe_medico', 'Informe Médico'),
        ('plan_tratamiento', 'Plan de Tratamiento'),
        ('poliza', 'Póliza'),
        ('receta', 'Receta'),
        ('resultados_estudios', 'Resultados de Estudios'),
        ('ticket_compra', 'Ticket de Compra'),
        ('otro', 'Otro'),
    ]

    id_documento = models.CharField(max_length=50, unique=True, default=generar_id_documento)  # Modificado
    tipo_descripcion = models.CharField(
        max_length=20, 
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento",
        default='otro'
    )
    fecha_subida = models.DateField(auto_now_add=True)  # Fecha automática al subir
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que sube el documento
    tipo_documento = models.CharField(max_length=10, blank=True, null=True)  # Tipo de documento (se llenará automáticamente)
    nombre_archivo = models.CharField(max_length=255)  # Nombre del archivo (requerido)
    archivo = models.FileField(upload_to='documentos/')  # Campo para el archivo físico
    tamaño = models.CharField(max_length=20, editable=False)  # Tamaño del archivo (se calculará automáticamente)
    ultima_modificacion = models.DateField(auto_now=True)  # Fecha de última modificación
    comentario = models.TextField(blank=True, null=True)  # Comentario opcional
    id_poliza = models.ForeignKey(Poliza, on_delete=models.SET_NULL, blank=True, null=True)  # Relación con pólizas (opcional)
    id_asegurado = models.ForeignKey(Asegurado, on_delete=models.SET_NULL, blank=True, null=True)  # Relación con asegurados (opcional)
    historial = models.TextField(blank=True, null=True)  # Historial de movimientos del archivo
    datos_xml = models.JSONField(blank=True, null=True)  # Campo para almacenar datos extraídos del XML

    def save(self, *args, **kwargs):
        if not self.id_documento:
            self.id_documento = generar_id_documento()

        if not self.nombre_archivo and self.archivo:
            self.nombre_archivo = self.archivo.name

        if self.archivo:
            self.tamaño = formato_tamaño(self.archivo.size)

            # Procesar XML si el archivo es de tipo XML
            if self.nombre_archivo.lower().endswith('.xml'):
                from .processors.xml_processor import CFDIProcessor
                from . import init_db
                
                db_session = init_db()  # Inicializar sesión SQLAlchemy
                processor = CFDIProcessor(db_session)
                self.datos_xml = processor.process(self.archivo)
                db_session.close()

        if not self.nombre_archivo:
            raise ValidationError("El nombre del archivo es obligatorio")

        # Determinar automáticamente el tipo de documento basado en la extensión del archivo
        extension = os.path.splitext(self.nombre_archivo)[1].lower().strip('.')
        self.tipo_documento = extension

        # Registrar cambios en el historial
        if self.pk:  # Si el documento ya existe
            original = Documento.objects.get(pk=self.pk)
            cambios = []
            if original.nombre_archivo != self.nombre_archivo:
                cambios.append(f"Nombre cambiado de '{original.nombre_archivo}' a '{self.nombre_archivo}'")
            if original.comentario != self.comentario:
                cambios.append(f"Comentario cambiado de '{original.comentario}' a '{self.comentario}'")
            if cambios:
                self.historial = (self.historial or '') + "\n".join(cambios) + "\n"

        super().save(*args, **kwargs)  # Llamar al método save original

    def procesar_documento(self):
        """Procesa el documento según su tipo"""
        if self.archivo and self.tipo_documento == 'xml':
            from .processors.xml_processor import CFDIProcessor
            from . import init_db
            
            db_session = init_db()
            processor = CFDIProcessor(db_session)
            self.datos_xml = processor.process(self.archivo)
            db_session.close()
            return processor

    def get_datos_xml(self):
        """Obtiene datos específicos del XML"""
        if self.datos_xml:
            from .processors.xml_processor import CFDIProcessor
            from . import init_db
            
            db_session = init_db()
            processor = CFDIProcessor(db_session)
            processor.data = self.datos_xml
            return processor
        return None

    def __str__(self):
        return f"{self.id_documento} - {self.nombre_archivo or 'Sin Nombre'}"
