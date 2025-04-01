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
    diagnostico_existente = forms.ModelChoiceField(
        queryset=Diagnosticos.objects.none(),
        required=False,
        label='Diagnóstico Existente'
    )
    diagnostico_nuevo = forms.CharField(
        required=False,
        label='Nuevo Diagnóstico'
    )
    diagnostico_tipo = forms.ChoiceField(
        choices=[
            ('existente', 'Seleccionar Existente'),
            ('nuevo', 'Crear Nuevo')
        ],
        initial='existente'
    )
    fecha_inicio_padecimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de Inicio del Padecimiento'
    )
    fecha_primera_atencion = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Fecha de Primera Atención'
    )

    class Meta:
        model = Diagnosticos
        fields = ['descripcion_diagnostico']

    def __init__(self, *args, **kwargs):
        asegurado_id = kwargs.pop('asegurado_id', None)
        super().__init__(*args, **kwargs)
        
        # Ocultar el campo descripcion_diagnostico
        self.fields['descripcion_diagnostico'].widget = forms.HiddenInput()
        
        if asegurado_id:
            try:
                asegurado = Asegurado.objects.get(id_asegurado=asegurado_id)
                self.fields['diagnostico_existente'].queryset = asegurado.diagnosticos_relacionados.all()
                
                # Imprimir los diagnósticos relacionados para verificar
                print(f"Diagnósticos relacionados para el asegurado {asegurado_id}: {self.fields['diagnostico_existente'].queryset}")
            except Asegurado.DoesNotExist:
                self.fields['diagnostico_existente'].queryset = Diagnosticos.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        diagnostico_tipo = cleaned_data.get('diagnostico_tipo')
        diagnostico_existente = cleaned_data.get('diagnostico_existente')
        diagnostico_nuevo = cleaned_data.get('diagnostico_nuevo')

        if diagnostico_tipo == 'existente' and not diagnostico_existente:
            raise forms.ValidationError('Debe seleccionar un diagnóstico existente.')
        elif diagnostico_tipo == 'nuevo' and not diagnostico_nuevo:
            raise forms.ValidationError('Debe ingresar un nuevo diagnóstico.')

        return cleaned_data
