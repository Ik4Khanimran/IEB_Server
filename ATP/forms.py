from django import forms
from .models import EngCheckpoint, CheckpointMap

class EngCheckpoint_form(forms.ModelForm):
    class Meta:
        model = EngCheckpoint
        fields = '__all__'

class CheckpointMap_form(forms.ModelForm):
    class Meta:
        model = CheckpointMap
        fields = '__all__'