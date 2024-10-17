from django import forms

class HireEmployeeForm(forms.Form):
    EMPLOYEE_TYPES = [
        ('fast_worker', 'Fast Worker (Lower skill, lower salary)'),
        ('perfectionist', 'Perfectionist (Higher skill, higher salary)'),
    ]
    HIRING_PROCESSES = [
        ('resume_only', 'Resume Only (Immediate hire, limited information)'),
        ('phone_interview', 'Phone Interview (1 day, partial skill revelation)'),
        ('live_coding', 'Live Coding Test (1 week, reveals coding skills)'),
        ('full_interview', 'Full Interview Process (1 month, most information)'),
    ]
    employee_type = forms.ChoiceField(choices=EMPLOYEE_TYPES, widget=forms.RadioSelect, initial='fast_worker')
    hiring_process = forms.ChoiceField(choices=HIRING_PROCESSES, widget=forms.RadioSelect, initial='resume_only')
