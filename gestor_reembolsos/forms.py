from django import forms
from gestor_asegurados.models import Asegurado, Diagnosticos, Poliza
from .models import Reembolso, Reclamacion

class ReembolsoForm(forms.ModelForm):
    class Meta:
        model = Reembolso
        fields = ['asegurado', 'poliza', 'monto_solicitado', 'comentarios']
        widgets = {
            'asegurado': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
                'onchange': 'cargarDiagnosticos(this.value)'
            }),
            'poliza': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'monto_solicitado': forms.NumberInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        # Verificar que todos los campos requeridos estén presentes
        required_fields = ['asegurado', 'poliza', 'monto_solicitado']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'Este campo es obligatorio')
        
        asegurado = cleaned_data.get('asegurado')
        poliza = cleaned_data.get('poliza')
        
        if asegurado and poliza and asegurado.id_poliza != poliza:
            raise forms.ValidationError(
                "La póliza seleccionada no corresponde al asegurado"
            )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asegurado'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'cargarDiagnosticos(this.value)'
        })
        self.fields['poliza'].widget.attrs.update({'class': 'form-select'})
        self.fields['monto_solicitado'].widget.attrs.update({'class': 'form-control'})
        self.fields['comentarios'].widget.attrs.update({'class': 'form-control'})

        # Hacer la póliza un campo oculto
        self.fields['poliza'].widget = forms.HiddenInput()
        self.fields['poliza'].required = True
        
        if 'asegurado' in self.data:
            try:
                asegurado_id = self.data.get('asegurado')
                asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
                self.fields['poliza'].initial = asegurado.id_poliza.id_poliza
            except (Asegurado.DoesNotExist, AttributeError):
                pass

class DiagnosticoReembolsoForm(forms.ModelForm):
    usar_existente = forms.BooleanField(required=False, initial=False)
    diagnostico_existente = forms.ModelChoiceField(
        queryset=Diagnosticos.objects.none(),
        required=False,
        empty_label="Seleccione un diagnóstico existente",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Diagnosticos
        fields = ['diagnostico', 'fecha_inicio_padecimiento', 'fecha_primera_atencion']
        widgets = {
            'diagnostico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del diagnóstico'
            }),
            'fecha_inicio_padecimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_primera_atencion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        asegurado_id = kwargs.pop('asegurado_id', None)
        super().__init__(*args, **kwargs)
        if asegurado_id:
            asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
            self.fields['diagnostico_existente'].queryset = asegurado.diagnosticos_relacionados.all()
