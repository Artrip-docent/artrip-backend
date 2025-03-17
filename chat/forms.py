from django import forms
from .models import Document, Exhibition, Gallery
class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['name']
class DocumentForm(forms.ModelForm):
    file = forms.FileField(required=True, help_text="텍스트 파일(.txt)을 선택하세요.")
    class Meta:
        model = Document
        fields = ['exhibition']

class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = ['gallery', 'title', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
