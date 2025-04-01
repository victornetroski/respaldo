from django.core.management.base import BaseCommand
import csv

from gestor_asegurados.models import Aseguradora

class Command(BaseCommand):
    help = 'Importa aseguradoras desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta del archivo CSV')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        with open(csv_file_path, encoding='utf-8-sig') as file:
            # Leer primera línea para verificar el contenido
            first_line = file.readline()
            self.stdout.write(self.style.SUCCESS(f"Primera línea: {first_line}"))
            
            # Regresar al inicio del archivo
            file.seek(0)
            
            # Detectar delimitador
            if ',' in first_line:
                delimiter = ','
            elif '\t' in first_line:
                delimiter = '\t'
            else:
                self.stdout.write(self.style.ERROR("No se pudo detectar el delimitador"))
                return

            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Mostrar las columnas encontradas
            self.stdout.write(self.style.SUCCESS(f"Columnas encontradas: {reader.fieldnames}"))
            
            # Identificar nombres de columnas
            id_field = next((f for f in reader.fieldnames if 'id' in f.lower()), None)
            nombre_field = next((f for f in reader.fieldnames if 'nombre' in f.lower() and 'corto' not in f.lower()), None)
            nombre_corto_field = next((f for f in reader.fieldnames if 'corto' in f.lower()), None)

            if not all([id_field, nombre_field, nombre_corto_field]):
                self.stdout.write(self.style.ERROR(
                    f"No se encontraron todas las columnas necesarias.\n"
                    f"ID field: {id_field}\n"
                    f"Nombre field: {nombre_field}\n"
                    f"Nombre corto field: {nombre_corto_field}"
                ))
                return

            count = 0
            for row in reader:
                try:
                    self.stdout.write(f"\nProcesando fila: {dict(row)}")
                    
                    # Verificar si ya existe
                    aseguradora, created = Aseguradora.objects.get_or_create(
                        id_aseguradora=row[id_field],
                        defaults={
                            'nombre': row[nombre_field],
                            'nombre_corto': row[nombre_corto_field]
                        }
                    )
                    
                    if created:
                        count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Creada aseguradora: {aseguradora.nombre}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'Aseguradora ya existe: {aseguradora.nombre}')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error importando aseguradora: {str(e)}\nDatos: {row}')
                    )
                    continue

            self.stdout.write(
                self.style.SUCCESS(f'Importación completada. {count} aseguradoras importadas.')
            )