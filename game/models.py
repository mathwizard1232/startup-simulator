from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    funds = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    is_perfectionist = models.BooleanField(default=False)
    skill_level = models.IntegerField(default=1)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    morale = models.IntegerField(default=100)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')

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
