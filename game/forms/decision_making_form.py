from django import forms

class DecisionMakingForm(forms.Form):
    STATUS_REPORT_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    OVERTIME_POLICY_CHOICES = [
        ('no_overtime', 'No Overtime'),
        ('optional', 'Optional Overtime'),
        ('mandatory', 'Mandatory Overtime'),
    ]
    
    status_report_frequency = forms.ChoiceField(choices=STATUS_REPORT_CHOICES)
    overtime_policy = forms.ChoiceField(choices=OVERTIME_POLICY_CHOICES)