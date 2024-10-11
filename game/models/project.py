from .company import Company
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    complexity = models.IntegerField(default=1)

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