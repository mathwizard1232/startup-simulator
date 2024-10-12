from django import forms
from ..models.employee import Employee

class AssignEmployeesForm(forms.Form):
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields['employees'].queryset = company.employees.all()
        if project:
            self.fields['employees'].initial = project.employees.all()