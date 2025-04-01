from django import forms
from .models import Documento
from gestor_asegurados.models import Asegurado, Poliza

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['archivo', 'tipo_descripcion', 'comentario', 'id_asegurado', 'id_poliza']
        labels = {
            'tipo_descripcion': 'Tipo de Documento',
            'id_asegurado': 'Asegurado',
            'id_poliza': 'Póliza'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_asegurado'].queryset = Asegurado.objects.all().order_by('nombre')
        self.fields['id_poliza'].queryset = Poliza.objects.all().order_by('numero_poliza')
        
        # Hacer los campos opcionales y agregar placeholders
        self.fields['id_asegurado'].required = False
        self.fields['id_poliza'].required = False
        self.fields['id_asegurado'].empty_label = "Seleccione un asegurado (opcional)"
        self.fields['id_poliza'].empty_label = "Seleccione una póliza (opcional)"
        self.fields['tipo_descripcion'].required = True
