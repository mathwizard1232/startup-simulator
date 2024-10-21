from django import forms
from ..models.project import Project
import logging

logger = logging.getLogger(__name__)

class CreateProjectForm(forms.ModelForm):
    INDUSTRY_TYPES = [
        ('FINTECH', 'Fintech'),
        ('GAME_DEV', 'Game Development'),
    ]

    COMPLEXITY_CHOICES = [
        ('SHODDY', 'Shoddy'),
        ('STANDARD', 'Standard Practice'),
        ('ADVANCED', 'Advanced'),
    ]

    DEADLINE_CHOICES = [
        ('standard', 'Standard'),
        ('aggressive', 'Aggressive'),
        ('cautious', 'Cautious'),
    ]
    industry = forms.ChoiceField(choices=INDUSTRY_TYPES, widget=forms.HiddenInput())
    required_features = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)  # defaulted, not sent
    optional_features = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)
    deadline_type = forms.ChoiceField(choices=DEADLINE_CHOICES)

    class Meta:
        model = Project
        fields = ['name', 'description', 'industry', 'deadline_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        industry = self.initial.get('industry') or self.data.get('industry')
        if industry:
            self.fields['required_features'].choices = self.get_required_features(industry)
            self.fields['optional_features'].choices = self.get_optional_features(industry)

    def get_required_features(self, industry):
        logger.info(f"Getting required features for industry: {industry}")
        if industry == 'FINTECH':
            return [
                ('login', 'Login System'),
                ('account_management', 'Account Management'),
                ('transaction_processing', 'Transaction Processing'),
            ]
        elif industry == 'GAME_DEV':
            return [
                ('game_engine', 'Game Engine'),
                ('character_system', 'Character System'),
                ('level_design', 'Level Design'),
            ]
        return []

    def get_optional_features(self, industry):
        if industry == 'FINTECH':
            return [
                ('credit_scoring', 'Credit Scoring'),
                ('fraud_detection', 'Fraud Detection'),
                ('investment_tools', 'Investment Tools'),
                ('crypto_integration', 'Cryptocurrency Integration'),
            ]
        elif industry == 'GAME_DEV':
            return [
                ('multiplayer', 'Multiplayer'),
                ('in_game_economy', 'In-Game Economy'),
                ('ai_opponents', 'AI Opponents'),
                ('vr_support', 'VR Support'),
            ]
        return []

    def clean(self):
        cleaned_data = super().clean()
        # Required features aren't sent but implied
        # Choices have both internal and display names, so we need to use the internal names
        required_features = [feature[0] for feature in self.get_required_features(cleaned_data.get('industry'))]
        cleaned_data['required_features'] = required_features
        optional_features = cleaned_data.get('optional_features', [])

        # Add complexity fields dynamically
        for feature in (required_features or []) + (optional_features or []):
            complexity_field = f'{feature}_complexity'
            self.fields[complexity_field] = forms.ChoiceField(choices=self.COMPLEXITY_CHOICES)
            cleaned_data[complexity_field] = self.data.get(complexity_field)

        logger.info(f"Cleaned data: {cleaned_data}")
        return cleaned_data
