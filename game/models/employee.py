from .company import Company
from .project import Project
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ..name_generator import generate_name
import random

class Employee(models.Model):
    EMPLOYEE_TYPES = [
        ('PERFECTIONIST', 'Perfectionist'),
        ('FAST_WORKER', 'Fast Worker'),
    ]

    name = models.CharField(max_length=100, default=generate_name)
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    # Skill attributes
    coding_speed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    coding_accuracy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    debugging = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    teamwork = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )

    # Perceived skill attributes
    perceived_coding_speed = models.CharField(max_length=20, default='unknown')
    perceived_coding_accuracy = models.CharField(max_length=20, default='unknown')
    perceived_debugging = models.CharField(max_length=20, default='unknown')
    perceived_teamwork = models.CharField(max_length=20, default='unknown')

    morale = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=75
    )
    productivity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=75
    )

    def __str__(self):
        return f"{self.name} ({self.get_employee_type_display()})"

    @staticmethod
    def get_perceived_skill(skill_value):
        if skill_value <= 2:
            return 'poor'
        elif skill_value <= 4:
            return 'below average'
        elif skill_value <= 6:
            return 'average'
        elif skill_value <= 8:
            return 'good'
        else:
            return 'excellent'

    def update_perceived_skills(self):
        self.perceived_coding_speed = self.get_perceived_skill(self.coding_speed)
        self.perceived_coding_accuracy = self.get_perceived_skill(self.coding_accuracy)
        self.perceived_debugging = self.get_perceived_skill(self.debugging)
        self.perceived_teamwork = self.get_perceived_skill(self.teamwork)
        self.save()

    def generate_initial_skills(self):
        if self.employee_type == 'FAST_WORKER':
            self.coding_speed = random.randint(6, 10)
            self.coding_accuracy = random.randint(1, 7)
        else:  # PERFECTIONIST
            self.coding_speed = random.randint(1, 7)
            self.coding_accuracy = random.randint(6, 10)
        
        self.debugging = random.randint(1, 10)
        self.teamwork = random.randint(1, 10)
        self.update_perceived_skills()
        self.save()

    def calculate_productivity(self):
        skill_average = (self.coding_speed + self.coding_accuracy + self.debugging + self.teamwork) / 4
        return (skill_average * self.morale) / 100  # Productivity is a value between 0 and 10

    def update_productivity(self):
        self.productivity = self.calculate_productivity()
        self.save()
