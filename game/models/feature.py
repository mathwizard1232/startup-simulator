from .project import Project
from django.db import models

class Feature(models.Model):
    FEATURE_STATE_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('TESTING', 'Testing'),
        ('COMPLETED', 'Completed'),
    ]
    
    COMPLEXITY_CHOICES = [
        ('SHODDY', 'Shoddy'),
        ('STANDARD', 'Standard Practice'),
        ('ADVANCED', 'Advanced'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20, choices=FEATURE_STATE_CHOICES, default='NOT_STARTED')
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='STANDARD')
    is_required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.project.name})"
