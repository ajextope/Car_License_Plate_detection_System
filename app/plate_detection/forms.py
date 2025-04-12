# plate_detection/forms.py

from django import forms
from .models import PlateImage

class PlateImageForm(forms.ModelForm):
    class Meta:
        model = PlateImage
        fields = ['image']