from django import forms
from .models import XMLFile

class XMLUploadForm(forms.Form):
    file = forms.FileField(label="Subir archivo XML")