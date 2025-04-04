# Generated by Django 5.1.7 on 2025-03-31 23:48

import gestor_asegurados.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestor_asegurados', '0007_alter_diagnosticos_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diagnosticoasegurado',
            name='fecha_inicio_padecimiento',
            field=gestor_asegurados.models.MexicanDateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='diagnosticoasegurado',
            name='fecha_primera_atencion',
            field=gestor_asegurados.models.MexicanDateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='diagnosticos',
            name='fecha_inicio_padecimiento',
            field=gestor_asegurados.models.MexicanDateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='diagnosticos',
            name='fecha_primera_atencion',
            field=gestor_asegurados.models.MexicanDateField(blank=True, null=True),
        ),
    ]
