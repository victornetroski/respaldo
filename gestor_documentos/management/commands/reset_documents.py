from django.core.management.base import BaseCommand
from gestor_documentos.models import Documento
from django.db import connection

class Command(BaseCommand):
    help = 'Restablece el listado de documentos y limpia referencias huérfanas'

    def handle(self, *args, **options):
        # Eliminar todos los documentos de la base de datos
        Documento.objects.all().delete()
        
        # Limpiar la carpeta media/documentos
        import os
        import shutil
        media_path = os.path.join('media', 'documentos')
        if os.path.exists(media_path):
            shutil.rmtree(media_path)
            os.makedirs(media_path)
        
        # Reiniciar la secuencia del ID si es necesario (PostgreSQL)
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT setval(pg_get_serial_sequence('gestor_documentos_documento', 'id'), 1, false);")
            except:
                pass  # Si no es PostgreSQL, ignorar

        self.stdout.write(self.style.SUCCESS('Documentos restablecidos exitosamente'))
