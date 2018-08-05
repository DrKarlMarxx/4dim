from django import forms
from .models import SensorValue

class MyModelForm(forms.ModelForm):
    class Meta:
        model = SensorValue
        fields = ['type']