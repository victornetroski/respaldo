from django.db import models
from datetime import datetime
import uuid
from django.utils import timezone

class MexicanDateField(models.DateField):
    def to_python(self, value):
        if value is None or isinstance(value, datetime):
            return value
        
        try:
            # Intenta primero el formato mexicano
            return datetime.strptime(value, '%d/%m/%Y').date()
        except (ValueError, TypeError):
            # Si falla, intenta el formato estándar
            return super().to_python(value)

class Aseguradora(models.Model):
    id_aseguradora = models.CharField(max_length=8, primary_key=True)  # Cambiado a CharField
    nombre = models.CharField(max_length=255)
    nombre_corto = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

import uuid

def generate_plan_id():
    return f"PLAN-{uuid.uuid4().hex[:8].upper()}"

def generate_poliza_id():
    return f"POL-{uuid.uuid4().hex[:8].upper()}"

class AseguradorasPlan(models.Model):
    id_plan = models.CharField(
        max_length=50,
        primary_key=True,
        default=generate_plan_id,
        editable=False
    )
    id_aseguradora = models.ForeignKey(
        'Aseguradora',
        on_delete=models.PROTECT,
        db_column='id_aseguradora'
    )
    nombre_plan = models.CharField(max_length=100)

    class Meta:
        db_table = 'gestor_asegurados_aseguradorasplan'
        verbose_name = 'Plan'
        verbose_name_plural = 'Planes'

    def __str__(self):
        return self.nombre_plan

class Poliza(models.Model):
    id_poliza = models.CharField(
        max_length=50,
        primary_key=True
    )
    id_aseguradora = models.ForeignKey(Aseguradora, on_delete=models.PROTECT)  # Relación con Aseguradora
    id_plan = models.ForeignKey(AseguradorasPlan, on_delete=models.PROTECT)  # Relación con Plan
    numero_poliza = models.CharField(max_length=50)  # Numero_Poliza
    fisica_moral = models.CharField(max_length=10)  # Fisica_Moral?
    contratante_moral = models.CharField(max_length=255)  # Contratante_Moral
    folio_mercantil = models.CharField(max_length=50)  # Folio_Mercantil
    objeto_social = models.TextField()  # Objeto_Social
    nombre = models.CharField(max_length=255)  # Nombre
    apellido_paterno = models.CharField(max_length=255)  # Apellido_Paterno
    apellido_materno = models.CharField(max_length=255)  # Apellido_Materno
    fecha_nacimiento = MexicanDateField()  # Fecha_Nacimiento
    lugar_nacimiento = models.CharField(max_length=255)  # Lugar_Nacimiento
    curp = models.CharField(max_length=18)  # CURP
    pais_nacimiento = models.CharField(max_length=100)  # Pais_Nacimiento
    nacionalidad = models.CharField(max_length=100)  # Nacionalidad
    rfc = models.CharField(max_length=13)  # RFC
    profesion = models.CharField(max_length=100)  # Profesion
    calle = models.CharField(max_length=255)  # Calle
    numero_exterior = models.CharField(max_length=10)  # Numero_Exterior
    numero_interior = models.CharField(max_length=10)  # Numero_Interior
    colonia = models.CharField(max_length=255)  # Colonia
    municipio_delegacion = models.CharField(max_length=255)  # Municipio_Delegacion
    entidad_federativa = models.CharField(max_length=255)  # Entidad_Federativa
    ciudad_poblacion = models.CharField(max_length=255)  # Ciudad_Poblacion
    codigo_postal = models.CharField(max_length=10)  # Codigo_Postal - Corregido 'maxlength' a 'max_length'
    telefono = models.CharField(max_length=15)  # Telefono
    email = models.EmailField(max_length=255)  # Email
    poliza_pdf = models.FileField(upload_to='polizas/')  # Poliza_Pdf
    gobierno = models.BooleanField(default=False)  # Gobierno?
    cargo = models.CharField(max_length=100)  # Cargo
    dependencia = models.CharField(max_length=255)  # Dependencia
    actua_nombre_propio = models.BooleanField(default=False)  # Actua_Nombre_Propio?
    titular_contratante = models.CharField(max_length=255)  # Titular_Contratante
    clabe = models.CharField(max_length=18)  # Clabe
    banco = models.CharField(max_length=100)  # Banco

    def __str__(self):
        return self.numero_poliza

class Asegurado(models.Model):
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
    ]
    
    TIPO_ASEGURADO_CHOICES = [
        ('Titular', 'Titular'),
        ('Conyuge', 'Conyuge'),
        ('Dependiente', 'Dependiente'),
    ]

    id_asegurado = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Identificador único alfanumérico del asegurado"
    )
    id_poliza = models.ForeignKey(Poliza, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=255)
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255)
    fecha_nacimiento = MexicanDateField()
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    rfc = models.CharField(max_length=13, blank=True, null=True)
    email = models.EmailField(max_length=255)
    telefono = models.CharField(max_length=15)
    titular_conyuge_dependiente = models.CharField(
        max_length=15,
        choices=TIPO_ASEGURADO_CHOICES,
        default='Titular'
    )

    @property
    def diagnosticos(self):
        """Obtiene los diagnósticos relacionados con este asegurado"""
        return self.diagnosticos_relacionados.all()

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"

class Diagnosticos(models.Model):
    id_diagnostico = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Identificador único alfanumérico del diagnóstico"
    )
    descripcion_diagnostico = models.CharField(max_length=255)
    asegurados = models.ManyToManyField(
        Asegurado,
        through='DiagnosticoAsegurado',
        related_name='diagnosticos'
    )
    fecha_inicio_padecimiento = MexicanDateField(null=True, blank=True)
    fecha_primera_atencion = MexicanDateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.descripcion_diagnostico

    class Meta:
        verbose_name = "Diagnostico"
        verbose_name_plural = "Diagnosticos"

class DiagnosticoAsegurado(models.Model):
    diagnostico = models.ForeignKey(Diagnosticos, on_delete=models.PROTECT)
    asegurado = models.ForeignKey(
        Asegurado, 
        on_delete=models.PROTECT,
        related_name='diagnosticos_relacionados'
    )
    fecha_inicio_padecimiento = MexicanDateField(null=True, blank=True)
    fecha_primera_atencion = MexicanDateField(null=True, blank=True)

    class Meta:
        unique_together = ('diagnostico', 'asegurado')