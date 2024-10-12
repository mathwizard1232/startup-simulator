from django import forms
from ..models.project import Project

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']