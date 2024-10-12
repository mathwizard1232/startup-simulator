from django import forms
from ..models.company import Company

class StartGameForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'industry']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['industry'].choices = Company.INDUSTRY_CHOICES
