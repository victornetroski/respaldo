# Generated by Django 5.1.7 on 2025-04-01 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestor_asegurados', '0008_alter_diagnosticoasegurado_fecha_inicio_padecimiento_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='diagnosticos',
            old_name='diagnostico',
            new_name='descripcion_diagnostico',
        ),
    ]
