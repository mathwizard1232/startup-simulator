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

class Employee(models.Model):
    name = models.CharField(max_length=100)
    is_perfectionist = models.BooleanField(default=False)
    skill_level = models.IntegerField(default=1)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    morale = models.IntegerField(default=100)
    productivity = models.IntegerField(default=100)

    def __str__(self):
        return self.name

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
        if self.company.industry == 'FINTECH':
            Feature.objects.create(name="Security Implementation", project=self)
            Feature.objects.create(name="Payment Processing", project=self)
        elif self.company.industry == 'GAME_DEV':
            Feature.objects.create(name="Graphics Engine", project=self)
            Feature.objects.create(name="Game Mechanics", project=self)
        Feature.objects.create(name="User Interface", project=self)

    def __str__(self):
        return self.name

class Feature(models.Model):
    FEATURE_STATE_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('TESTING', 'Testing'),
        ('COMPLETED', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20, choices=FEATURE_STATE_CHOICES, default='NOT_STARTED')

    def __str__(self):
        return f"{self.name} ({self.project.name})"

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
