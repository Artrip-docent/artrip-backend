from django import forms
from .models import Gallery, Exhibition

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '갤러리 이름을 입력하세요'}),
        }
        labels = {
            'name': '갤러리 이름'
        }

class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = ['gallery', 'title', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': '전시회 제목을 입력하세요'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'gallery': '갤러리',
            'title': '전시회 제목',
            'start_date': '시작일',
            'end_date': '종료일',
        }
