from .project import Project
from .feature import Feature
from django.db import models

class Bug(models.Model):
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='bugs', null=True, blank=True)
    STATE_CHOICES = [
        ('UNDETECTED', 'Undetected'),
        ('DETECTED', 'Detected'),
        ('FIXED', 'Fixed'),
    ]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='UNDETECTED')
    affected_features = models.ManyToManyField(Feature, related_name='affecting_bugs')

    def __str__(self):
        return f"Bug in {self.project.name}: {self.description[:50]}..."