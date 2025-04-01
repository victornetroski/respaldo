import csv
from django.core.management.base import BaseCommand
from gestor_asegurados.models import Diagnosticos, Asegurado, DiagnosticoAsegurado
from django.utils import timezone
from datetime import datetime
from django.db import transaction

class Command(BaseCommand):
    help = 'Importa diagnósticos desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV')

    def parse_fecha(self, fecha_str):
        """Convierte string de fecha en formato mexicano a objeto datetime"""
        try:
            return datetime.strptime(fecha_str.strip(), '%d/%m/%Y').date()
        except:
            return None

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        diagnosticos_creados = 0
        relaciones_creadas = 0
        errores = []

        try:
            # Abrimos con utf-8-sig para manejar el BOM
            with open(csv_file, encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                self.stdout.write(self.style.WARNING(f'Columnas detectadas: {reader.fieldnames}'))
                
                for row in reader:
                    try:
                        with transaction.atomic():
                            # Limpiamos las llaves del diccionario
                            row = {k.strip().lower(): v.strip() for k, v in row.items() if k and v}
                            
                            id_diagnostico = row.get('id_diagnostico')
                            id_asegurado = row.get('id_asegurado')
                            nombre_diagnostico = row.get('nombre_diagnostico')
                            fecha_inicio = self.parse_fecha(row.get('fecha_inicio_padecimiento', ''))
                            fecha_primera = self.parse_fecha(row.get('fecha_primera_atencion', ''))
                            
                            if not all([id_diagnostico, id_asegurado, nombre_diagnostico, """fecha_inicio, fecha_primera"""]):
                                raise ValueError(f"Datos incompletos: {row}")

                            # Verificar que existe el asegurado
                            try:
                                asegurado = Asegurado.objects.get(id_asegurado=id_asegurado)
                            except Asegurado.DoesNotExist:
                                raise ValueError(f"Asegurado no encontrado: {id_asegurado}")

                            # Crear o actualizar diagnóstico
                            diagnostico, created = Diagnosticos.objects.update_or_create(
                                id_diagnostico=id_diagnostico,
                                defaults={
                                    'diagnostico': nombre_diagnostico,
                                }
                            )

                            if created:
                                diagnosticos_creados += 1
                                self.stdout.write(self.style.SUCCESS(
                                    f'Creado diagnóstico: {id_diagnostico}'
                                ))

                            # Crear o actualizar la relación
                            DiagnosticoAsegurado.objects.update_or_create(
                                diagnostico=diagnostico,
                                asegurado=asegurado,
                                defaults={
                                    'fecha_inicio_padecimiento': fecha_inicio,
                                    'fecha_primera_atencion': fecha_primera,
                                }
                            )
                            relaciones_creadas += 1

                    except Exception as e:
                        error_msg = f"Error en línea {reader.line_num}: {str(e)}"
                        errores.append(error_msg)
                        self.stdout.write(self.style.ERROR(f"{error_msg}\nDatos: {row}"))

            self.stdout.write(self.style.SUCCESS(
                f'\nImportación completada:\n'
                f'- Diagnósticos creados/actualizados: {diagnosticos_creados}\n'
                f'- Relaciones creadas/actualizadas: {relaciones_creadas}\n'
                f'- Errores encontrados: {len(errores)}'
            ))

            if errores:
                self.stdout.write(self.style.WARNING('\nErrores encontrados:'))
                for error in errores:
                    self.stdout.write(self.style.WARNING(error))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al abrir el archivo: {str(e)}'))
