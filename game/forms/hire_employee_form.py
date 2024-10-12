from django import forms

class HireEmployeeForm(forms.Form):
    EMPLOYEE_TYPES = [
        ('fast_worker', 'Fast Worker (Lower skill, lower salary)'),
        ('perfectionist', 'Perfectionist (Higher skill, higher salary)'),
    ]
    employee_type = forms.ChoiceField(choices=EMPLOYEE_TYPES, widget=forms.RadioSelect, initial='fast_worker')
