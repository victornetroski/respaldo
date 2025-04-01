from django.db import models
from django.contrib.auth.models import User
from gestor_asegurados.models import Asegurado, Poliza, Diagnosticos
from gestor_documentos.models import Documento

class Reembolso(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('pagado', 'Pagado'),
    ]

    id_reembolso = models.AutoField(primary_key=True)
    fecha_solicitud = models.DateField(auto_now_add=True)
    asegurado = models.ForeignKey(Asegurado, on_delete=models.CASCADE)
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE)
    monto_solicitado = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.CASCADE)
    documentos = models.ManyToManyField(Documento, through='DocumentoReembolso')
    comentarios = models.TextField(blank=True, null=True)
    pdf_generado = models.FileField(
        upload_to='reembolsos/',
        null=True,
        blank=True,
        verbose_name="PDF del reembolso"
    )

    def __str__(self):
        return f"Reembolso {self.id_reembolso} - {self.asegurado}"

class DocumentoReembolso(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('factura', 'Factura'),
        ('receta', 'Receta Médica'),
        ('estudios', 'Estudios'),
        ('informe', 'Informe Médico'),
        ('otro', 'Otro'),
    ]

    reembolso = models.ForeignKey(Reembolso, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    fecha_asociacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reembolso', 'documento']

class Reclamacion(models.Model):
    id_reclamacion = models.AutoField(primary_key=True)
    id_diagnostico = models.ForeignKey(Diagnosticos, on_delete=models.PROTECT)
    inicial_complementaria = models.BooleanField(
        default=False,
        verbose_name="¿Es complementaria?",
        help_text="Marcar si esta reclamación es complementaria a una anterior"
    )
    cantidad_partidas = models.IntegerField(
        verbose_name="Cantidad de partidas",
        help_text="Número de partidas en la reclamación"
    )
    abierta = models.BooleanField(
        default=True,
        verbose_name="¿Reclamación abierta?",
        help_text="Indica si la reclamación sigue abierta o ya está cerrada"
    )
    reembolso = models.ForeignKey(
        Reembolso, 
        on_delete=models.CASCADE,
        related_name='reclamaciones'
    )
    facturas = models.ManyToManyField(
        Documento,
        through='FacturaReclamacion',
        related_name='reclamaciones'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reclamación {self.id_reclamacion} - {self.id_diagnostico}"

    class Meta:
        verbose_name = "Reclamación"
        verbose_name_plural = "Reclamaciones"

class FacturaReclamacion(models.Model):
    reclamacion = models.ForeignKey(Reclamacion, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.PROTECT)
    importe = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Importe de la factura"
    )
    fecha_asociacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Factura de Reclamación"
        verbose_name_plural = "Facturas de Reclamaciones"
        unique_together = ['reclamacion', 'documento']

    def __str__(self):
        return f"Factura {self.documento.id_documento} - Reclamación {self.reclamacion.id_reclamacion}"
