from django.core.management.base import BaseCommand
from gestor_asegurados.models import Aseguradora, AseguradorasPlan
from django.db import transaction
import csv

class Command(BaseCommand):
    help = 'Importa planes de aseguradoras desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta del archivo CSV')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        count_created = 0

        try:
            with open(csv_file_path, encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                self.stdout.write(f"Columnas encontradas: {reader.fieldnames}")

                for row in reader:
                    with transaction.atomic():
                        try:
                            # Primero verificamos que la aseguradora exista
                            aseguradora = Aseguradora.objects.get(
                                id_aseguradora=row['id_aseguradora'].strip()
                            )

                            # Luego creamos el plan
                            plan = AseguradorasPlan.objects.create(
                                id_plan=row['id_plan'].strip(),
                                id_aseguradora=aseguradora,  # Aquí cambiamos la forma de asignar
                                nombre_plan=row['nombre_plan'].strip()
                            )

                            count_created += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Creado plan: {plan.nombre_plan} "
                                    f"con ID: {plan.id_plan}"
                                )
                            )

                        except KeyError as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Error: Columna no encontrada en el CSV: {e}"
                                )
                            )
                            continue
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Error procesando fila: {row}\nError: {str(e)}"
                                )
                            )
                            continue

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nImportación completada. {count_created} planes creados."
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"No se encontró el archivo: {csv_file_path}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error durante la importación: {str(e)}")
            )