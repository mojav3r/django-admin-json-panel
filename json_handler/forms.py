from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import JSONData


class JSONDataForm(forms.ModelForm):
    class Meta:
        model = JSONData
        fields = ('author', 'upload', 'data')

        widgets = {
            'data': JSONEditorWidget
        }
