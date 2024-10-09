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

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    is_perfectionist = models.BooleanField(default=False)
    skill_level = models.IntegerField(default=1)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    morale = models.IntegerField(default=100)
    productivity = models.IntegerField(default=100)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
    complexity = models.IntegerField(default=1)
    
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
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='features')
    STATE_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='NOT_STARTED')

    def __str__(self):
        return f"{self.name} ({self.project.name})"

class Bug(models.Model):
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    STATE_CHOICES = [
        ('UNDETECTED', 'Undetected'),
        ('DETECTED', 'Detected'),
        ('FIXED', 'Fixed'),
    ]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='UNDETECTED')
    affected_features = models.ManyToManyField(Feature, related_name='affecting_bugs')

    def __str__(self):
        return f"Bug in {self.project.name}: {self.description[:50]}..."
