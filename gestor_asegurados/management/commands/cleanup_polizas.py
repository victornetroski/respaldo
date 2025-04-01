from django.core.management.base import BaseCommand
from gestor_asegurados.models import Poliza

class Command(BaseCommand):
    help = 'Elimina pólizas con IDs auto-generados'

    def handle(self, *args, **options):
        count, _ = Poliza.objects.filter(id_poliza__startswith='POL-').delete()
        self.stdout.write(
            self.style.SUCCESS(f"Se eliminaron {count} pólizas auto-generadas.")
        )