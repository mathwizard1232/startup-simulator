from .company import Company
from .project import Project
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from ..name_generator import generate_name
import random
import logging
from django.contrib.postgres.fields import ArrayField
from ..utils.skill_utils import get_perceived_skill

logger = logging.getLogger(__name__)

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

    # defined in personality_traits.py
    personality_traits_string = models.TextField(blank=True, default='')
    perceived_personality_traits_string = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.get_employee_type_display()})"

    @property
    def personality_traits(self):
        logger.info(f"Personality traits for {self.name}: {self.personality_traits_string}")
        return self.personality_traits_string.split(',')

    @property
    def perceived_personality_traits(self):
        logger.info(f"Perceived personality traits for {self.name}: {self.perceived_personality_traits_string}")
        return self.perceived_personality_traits_string.split(',')

    @property
    def perceived_personality_traits_human_readable(self):
        return [' '.join(word.capitalize() for word in trait.split('_')) for trait in self.perceived_personality_traits]

    def get_perceived_skill(self, skill_value):
        return get_perceived_skill(skill_value)

    def update_perceived_skills(self, process_type):
        if process_type == 'full_interview':
            self.perceived_coding_speed = self.get_perceived_skill(self.coding_speed)
            self.perceived_coding_accuracy = self.get_perceived_skill(self.coding_accuracy)
            self.perceived_debugging = self.get_perceived_skill(self.debugging)
            self.perceived_teamwork = self.get_perceived_skill(self.teamwork)
        elif process_type == 'live_coding':
            self.perceived_coding_speed = self.get_perceived_skill(self.coding_speed)
            self.perceived_coding_accuracy = self.get_perceived_skill(self.coding_accuracy)
        elif process_type == 'phone_interview':
            self.perceived_teamwork = self.get_perceived_skill(self.teamwork)
        self.save()

    def update_perceived_personality_traits(self, process_type):
        if process_type == 'full_interview' or process_type == 'phone_interview':
            self.perceived_personality_traits_string = self.personality_traits_string
        if process_type == 'resume':
            if random.randint(1, 100) <= 50:
                # 50% chance to reveal a single personality trait
                self.perceived_personality_traits_string = self.personality_traits[0]
        self.save()

    def generate_initial_skills(self, process_type):
        if self.employee_type == 'FAST_WORKER':
            self.coding_speed = random.randint(6, 10)
            self.coding_accuracy = random.randint(1, 7)
        else:  # PERFECTIONIST
            self.coding_speed = random.randint(1, 7)
            self.coding_accuracy = random.randint(6, 10)
        
        self.debugging = random.randint(1, 10)
        self.teamwork = random.randint(1, 10)
        self.update_perceived_skills(process_type)
        self.save()

    def calculate_productivity(self):
        logger.info(f"Calculating productivity for {self.name}")
        skill_average = (self.coding_speed + self.coding_accuracy + self.debugging + self.teamwork) / 4
        logger.info(f"Skill average: {skill_average}; morale: {self.morale}")
        # Productivity is a value between 0 and 100, while skills are a value between 0 and 10.
        # Because morale is 0-100, and skills are 0-10, we need to divide by 10 to get a
        # productivity value that scales correctly with morale.
        productivity = (skill_average * self.morale) / 10
        logger.info(f"Productivity: {productivity}")
        return productivity

    def update_productivity(self):
        self.productivity = self.calculate_productivity()
        self.save()
