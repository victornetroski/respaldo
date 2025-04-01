from django.core.management.base import BaseCommand
from gestor_asegurados.models import Aseguradora, AseguradorasPlan, Poliza
from django.db.models import CharField
from django.db.models.functions import Cast
from django.db import connection

class Command(BaseCommand):
    help = 'Limpia la base de datos de registros duplicados'

    def handle(self, *args, **options):
        try:
            # Mostrar estado actual
            self.stdout.write("\nEstado actual de la base de datos:")
            
            # Obtener conteos iniciales
            polizas_count = Poliza.objects.count()
            planes_count = AseguradorasPlan.objects.count()
            aseguradoras_count = Aseguradora.objects.count()

            # Mostrar información actual
            self.stdout.write(f"\nPólizas: {polizas_count}")
            self.stdout.write(f"Planes: {planes_count}")
            self.stdout.write(f"Aseguradoras: {aseguradoras_count}")

            # Confirmar antes de eliminar
            self.stdout.write("\n¿Desea proceder con la eliminación? (s/n)")
            confirmacion = input()
            
            if confirmacion.lower() != 's':
                self.stdout.write(self.style.WARNING("\nOperación cancelada"))
                return

            # Eliminar registros usando SQL directo
            self.stdout.write("\nEliminando registros...")
            
            with connection.cursor() as cursor:
                # Desactivar temporalmente la revisión de claves foráneas
                cursor.execute('PRAGMA foreign_keys=OFF;')
                
                # Eliminar registros
                cursor.execute('DELETE FROM gestor_asegurados_poliza;')
                cursor.execute('DELETE FROM gestor_asegurados_aseguradorasplan;')
                cursor.execute('DELETE FROM gestor_asegurados_aseguradora;')
                
                # Reactivar la revisión de claves foráneas
                cursor.execute('PRAGMA foreign_keys=ON;')

            self.stdout.write(f"Eliminadas {polizas_count} pólizas")
            self.stdout.write(f"Eliminados {planes_count} planes")
            self.stdout.write(f"Eliminadas {aseguradoras_count} aseguradoras")
            
            self.stdout.write(self.style.SUCCESS("\nBase de datos limpiada exitosamente"))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\nError durante la limpieza: {str(e)}")
            )
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))