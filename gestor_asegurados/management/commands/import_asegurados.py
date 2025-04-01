from django.core.management.base import BaseCommand
from django.db import transaction
from gestor_asegurados.models import Asegurado, Poliza
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa asegurados desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Ruta al archivo CSV',
            nargs='?',
            default=None
        )

    def normalize_header(self, header):
        # Convertir a minúsculas y eliminar espacios
        return header.lower().strip()

    def clean_header(self, header):
        """Limpia el encabezado de caracteres especiales y BOM"""
        return header.replace('\ufeff', '').lower().strip()

    def get_value(self, row, field, default=''):
        """Obtiene el valor de un campo del CSV, ignorando mayúsculas/minúsculas y BOM"""
        field = field.replace('\ufeff', '').lower().strip()
        for key in row.keys():
            clean_key = key.replace('\ufeff', '').lower().strip()
            if clean_key == field:
                return row[key] or default
        self.stdout.write(self.style.WARNING(f"Campo no encontrado: {field}"))
        return default

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs.get('csv_file')
        if not csv_file_path:
            self.stdout.write(self.style.ERROR('Por favor, proporciona la ruta al archivo CSV'))
            return
        
        # Intentar diferentes codificaciones
        encodings = ['utf-8-sig', 'utf-8', 'latin1', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(csv_file_path, encoding=encoding) as file:
                    # Leer la primera línea para verificar la codificación
                    header = file.readline()
                    self.stdout.write(f"Intentando con codificación: {encoding}")
                    self.stdout.write(f"Encabezados encontrados: {header.strip()}")
                    break
            except UnicodeDecodeError:
                continue
        else:
            self.stdout.write(self.style.ERROR('No se pudo leer el archivo CSV con ninguna codificación'))
            return

        # Realizar la importación
        with open(csv_file_path, encoding=encoding) as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            self.stdout.write(f"Columnas encontradas: {headers}")
            
            total_rows = sum(1 for row in reader)
            file.seek(0)
            reader = csv.DictReader(file)
            
            successful = 0
            failed = 0
            skipped = 0
            
            for row in reader:
                try:
                    with transaction.atomic():
                        # Obtener id_asegurado directamente usando get_value
                        id_asegurado = self.get_value(row, 'id_asegurado')
                        
                        if not id_asegurado:
                            self.stdout.write(self.style.ERROR(
                                f"ID Asegurado vacío en la línea {reader.line_num}"
                            ))
                            failed += 1
                            continue

                        id_poliza = self.get_value(row, 'id_poliza')
                        
                        self.stdout.write(f"\nProcesando registro:")
                        self.stdout.write(f"ID Asegurado: {id_asegurado}")
                        self.stdout.write(f"ID Póliza: {id_poliza}")
                        
                        # Verificar si existe la póliza
                        try:
                            poliza = Poliza.objects.get(id_poliza=id_poliza)
                        except Poliza.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Póliza no encontrada: {id_poliza}"))
                            skipped += 1
                            continue

                        # Preparar los datos
                        defaults = {
                            'id_poliza': poliza,
                            'nombre': self.get_value(row, 'nombre', '').strip().upper(),
                            'apellido_paterno': self.get_value(row, 'apellido_paterno', '').strip().upper(),
                            'apellido_materno': self.get_value(row, 'apellido_materno', '').strip().upper(),
                            'genero': self.get_value(row, 'genero', '').strip(),
                            'rfc': self.get_value(row, 'rfc', '').strip() or None,
                            'email': self.get_value(row, 'email', '').strip(),
                            'telefono': self.get_value(row, 'telefono', '').strip(),
                        }

                        # Manejar tipo de asegurado
                        tipo = self.get_value(row, 'titular_conyuge_dependiente', '').strip()
                        if tipo.lower() in ['titular', 'conyuge', 'dependiente']:
                            defaults['titular_conyuge_dependiente'] = tipo.capitalize()
                        else:
                            defaults['titular_conyuge_dependiente'] = 'Titular'

                        # Manejar la fecha de nacimiento
                        fecha_nacimiento = self.get_value(row, 'fecha_nacimiento', '').strip()
                        if fecha_nacimiento:
                            try:
                                defaults['fecha_nacimiento'] = datetime.strptime(
                                    fecha_nacimiento, '%d/%m/%Y'
                                ).date()
                            except ValueError:
                                self.stdout.write(self.style.WARNING(
                                    f"Fecha inválida: {fecha_nacimiento}"
                                ))
                                failed += 1
                                continue

                        # Crear o actualizar el asegurado
                        asegurado, created = Asegurado.objects.update_or_create(
                            id_asegurado=id_asegurado,
                            defaults=defaults
                        )
                        
                        successful += 1
                        action = 'Creado' if created else 'Actualizado'
                        self.stdout.write(self.style.SUCCESS(
                            f'{action} asegurado: {asegurado.nombre} {asegurado.apellido_paterno}'
                        ))
                        
                except Exception as e:
                    failed += 1
                    self.stdout.write(self.style.ERROR(
                        f"Error en línea {reader.line_num}: {str(e)}"
                    ))

            self.stdout.write(self.style.SUCCESS(
                f'\nImportación completada:\n'
                f'- Registros exitosos: {successful}\n'
                f'- Registros saltados: {skipped}\n'
                f'- Registros fallidos: {failed}\n'
                f'- Total procesados: {total_rows}'
            ))
