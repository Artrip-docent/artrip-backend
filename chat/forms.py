from django import forms
from .models import Document
from exhibition.models import Exhibition # Exhibition 모델 임포트

class DocumentForm(forms.ModelForm):
    file = forms.FileField(required=True, help_text="텍스트 파일(.txt)을 선택하세요.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # exhibition 필드의 쿼리셋을 역순으로 정렬
        self.fields['exhibition'].queryset = Exhibition.objects.all().order_by('-id')

    class Meta:
        model = Document
        fields = ['exhibition']
        widgets = {
            'exhibition': forms.Select(attrs={'class': 'select2-field form-control'}),
        }