from django.core.management.base import BaseCommand
from gestor_asegurados.models import Poliza, Aseguradora, AseguradorasPlan
from django.db import transaction
from datetime import datetime
import csv

class Command(BaseCommand):
    help = 'Importa pólizas desde un archivo CSV'

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
                            # Verificar aseguradora y plan
                            aseguradora = Aseguradora.objects.get(
                                id_aseguradora=row['id_aseguradora'].strip()
                            )
                            
                            plan = AseguradorasPlan.objects.get(
                                nombre_plan=row['nombre_plan'].strip(),
                                id_aseguradora=aseguradora
                            )

                            # Convertir fecha
                            fecha_nacimiento = datetime.strptime(
                                row['fecha_nacimiento'].strip(), 
                                '%d/%m/%Y'
                            ).date()

                            # Crear póliza
                            poliza = Poliza.objects.create(
                                id_poliza=row['id_poliza'].strip(),  # Use CSV's ID
                                id_aseguradora=aseguradora,
                                id_plan=plan,
                                numero_poliza=row['numero_poliza'].strip(),
                                fisica_moral=row['fisica_moral'].strip(),
                                contratante_moral=row['contratante_moral'].strip(),
                                folio_mercantil=row['folio_mercantil'].strip(),
                                objeto_social=row['objeto_social'].strip(),
                                nombre=row['nombre'].strip(),
                                apellido_paterno=row['apellido_paterno'].strip(),
                                apellido_materno=row['apellido_materno'].strip(),
                                fecha_nacimiento=fecha_nacimiento,
                                lugar_nacimiento=row['lugar_nacimiento'].strip(),
                                curp=row['curp'].strip(),
                                pais_nacimiento=row['pais_nacimiento'].strip(),
                                nacionalidad=row['nacionalidad'].strip(),
                                rfc=row['rfc'].strip(),
                                profesion=row['profesion'].strip(),
                                calle=row['calle'].strip(),
                                numero_exterior=row['numero_exterior'].strip(),
                                numero_interior=row['numero_interior'].strip(),
                                colonia=row['colonia'].strip(),
                                municipio_delegacion=row['municipio_delegacion'].strip(),
                                entidad_federativa=row['entidad_federativa'].strip(),
                                ciudad_poblacion=row['ciudad_poblacion'].strip(),
                                codigo_postal=row['codigo_postal'].strip(),
                                telefono=row['telefono'].strip(),
                                email=row['email'].strip(),
                                gobierno=row['gobierno'].strip().lower() == 'true',
                                cargo=row['cargo'].strip(),
                                dependencia=row['dependencia'].strip(),
                                actua_nombre_propio=row['actua_nombre_propio'].strip().lower() == 'true',
                                titular_contratante=row['titular_contratante'].strip(),
                                clabe=row['clabe'].strip(),
                                banco=row['banco'].strip()
                            )

                            count_created += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Creada póliza: {poliza.id_poliza}"
                                )
                            )

                        except (Aseguradora.DoesNotExist, AseguradorasPlan.DoesNotExist) as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Error: Aseguradora o Plan no existe para la fila: {row}"
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
                        f"\nImportación completada. {count_created} pólizas creadas."
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