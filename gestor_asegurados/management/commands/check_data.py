from django.core.management.base import BaseCommand
from gestor_asegurados.models import Aseguradora, AseguradorasPlan

class Command(BaseCommand):
    help = 'Verifica los datos existentes'

    def handle(self, *args, **options):
        # Verificar aseguradoras
        aseguradoras = Aseguradora.objects.all()
        self.stdout.write(f"Aseguradoras encontradas: {aseguradoras.count()}")
        for a in aseguradoras:
            self.stdout.write(f"- ID: {a.id_aseguradora}, Nombre: {a.nombre}")

        # Verificar planes
        planes = AseguradorasPlan.objects.all()
        self.stdout.write(f"\nPlanes encontrados: {planes.count()}")
        for p in planes:
            self.stdout.write(f"- ID: {p.id_plan}, Nombre: {p.nombre_plan}")