from django import forms
from .models import Asegurado, Diagnosticos, DiagnosticoAsegurado

class AseguradoForm(forms.ModelForm):
    diagnosticos = forms.ModelMultipleChoiceField(
        queryset=Diagnosticos.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '5',  # Muestra 5 opciones a la vez
        })
    )

    class Meta:
        model = Asegurado
        fields = [
            'id_asegurado', 'id_poliza', 'nombre', 'apellido_paterno',
            'apellido_materno', 'fecha_nacimiento', 'genero', 'rfc',
            'email', 'telefono', 'titular_conyuge_dependiente'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un asegurado existente
        if self.instance.pk:
            # Preseleccionar los diagnósticos existentes
            self.initial['diagnosticos'] = self.instance.diagnosticos.all()

    def save(self, commit=True):
        asegurado = super().save(commit=commit)
        if commit:
            # Limpiar diagnósticos existentes y agregar los nuevos
            DiagnosticoAsegurado.objects.filter(asegurado=asegurado).delete()
            for diagnostico in self.cleaned_data['diagnosticos']:
                DiagnosticoAsegurado.objects.create(
                    asegurado=asegurado,
                    diagnostico=diagnostico,
                    fecha_inicio_padecimiento=diagnostico.fecha_inicio_padecimiento or timezone.now().date(),
                    fecha_primera_atencion=diagnostico.fecha_primera_atencion or timezone.now().date()
                )
        return asegurado
