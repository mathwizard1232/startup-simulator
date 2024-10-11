from django.db import models

class Company(models.Model):
    INDUSTRY_CHOICES = [
        ('FINTECH', 'Fintech'),
        ('GAME_DEV', 'Game Development'),
    ]
    name = models.CharField(max_length=100)
    funds = models.DecimalField(max_digits=12, decimal_places=2)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    status_report_frequency = models.CharField(max_length=20, default='weekly', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    overtime_policy = models.CharField(max_length=20, default='no_overtime', choices=[
        ('no_overtime', 'No Overtime'),
        ('optional', 'Optional Overtime'),
        ('mandatory', 'Mandatory Overtime'),
    ])
    GAME_STATUS_CHOICES = [
        ('ONGOING', 'Ongoing'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
    ]
    game_status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='ONGOING')
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    funds_history = models.TextField(default='[]')
    revenue_history = models.TextField(default='[]')

    def __str__(self):
        return self.name
