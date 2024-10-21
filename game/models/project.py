from .company import Company
from django.db import models
from django.utils import timezone
from datetime import timedelta

PROJECT_TYPES = [
    ('FINTECH', 'Fintech'),
    ('GAME_DEV', 'Game Development'),
]

DEADLINE_TYPES = [
    ('standard', 'Standard'),
    ('aggressive', 'Aggressive'),
    ('cautious', 'Cautious'),
]

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    complexity = models.IntegerField(default=1)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    deadline_type = models.CharField(max_length=20, choices=DEADLINE_TYPES, default='standard')
    deadline = models.DateTimeField(null=True, blank=True)

    @property
    def state(self):
        feature_states = set(self.features.values_list('state', flat=True))
        
        if not feature_states or feature_states == {'NOT_STARTED'}:
            return 'NOT_STARTED'
        elif 'IN_PROGRESS' in feature_states:
            return 'IN_PROGRESS'
        elif 'TESTING' in feature_states and 'COMPLETED' in feature_states and len(feature_states) == 2:
            return 'TESTING'
        elif feature_states == {'COMPLETED'}:
            return 'COMPLETED'
        else:
            return 'IN_PROGRESS'  # Default to IN_PROGRESS for any other combination

    @property
    def completed(self):
        return self.state == 'COMPLETED'

    def generate_industry_specific_features(self):
        # Prevent circular import by importing Feature here
        from .feature import Feature
        if self.company.industry == 'FINTECH':
            Feature.objects.create(name="Security Implementation", project=self)
            Feature.objects.create(name="Payment Processing", project=self)
        elif self.company.industry == 'GAME_DEV':
            Feature.objects.create(name="Graphics Engine", project=self)
            Feature.objects.create(name="Game Mechanics", project=self)
        Feature.objects.create(name="User Interface", project=self)

    def __str__(self):
        return self.name

    def set_deadline(self):
        if self.deadline_type == 'standard':
            self.deadline = timezone.now() + timedelta(days=30)
        elif self.deadline_type == 'aggressive':
            self.deadline = timezone.now() + timedelta(days=20)
        elif self.deadline_type == 'cautious':
            self.deadline = timezone.now() + timedelta(days=45)
        self.save()

    def is_past_deadline(self):
        return timezone.now() > self.deadline if self.deadline else False

    def time_pressure(self):
        if not self.deadline:
            return 0
        time_left = (self.deadline - timezone.now()).days
        if time_left <= 0:
            return 1
        elif time_left <= 7:
            return 0.8
        elif time_left <= 14:
            return 0.5
        else:
            return 0.2
