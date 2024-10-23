from django.test import TestCase
from django.urls import reverse
from game.models import Company, Employee
from game.views.decision_views import DecisionMakingView
import logging

logger = logging.getLogger(__name__)

class DecisionMakingTestCase(TestCase):
    def setUp(self):
        logger.info("DecisionMakingTestCase.setUp called")
        self.company = Company.objects.create(
            name="Test Company",
            funds=100000,
            industry='FINTECH',
            status_report_frequency='weekly',
            overtime_policy='no_overtime'
        )
        logger.info(f"Company created: {self.company}; id: {self.company.id}")
        self.employee = Employee.objects.create(
            name="Test Employee",
            company=self.company,
            employee_type="FAST_WORKER",
            morale=75,
            productivity=75
        )

    def test_decision_making(self):
        view = DecisionMakingView()
        
        decisions = [
            ('daily', 'mandatory'),
            ('weekly', 'optional'),
            ('monthly', 'none'),
            ('daily', 'none'),
            ('weekly', 'mandatory'),
            ('monthly', 'optional')
        ]
        
        for status_report, overtime in decisions:
            with self.subTest(status_report=status_report, overtime=overtime):
                view.apply_decision_effects(self.company, status_report, overtime)
                
                # Refresh company from database
                self.company.refresh_from_db()
                
                # Check that company decisions are updated correctly
                self.assertEqual(self.company.status_report_frequency, status_report)
                self.assertEqual(self.company.overtime_policy, overtime)

    def test_decision_making_view(self):
        url = reverse('decision_making')
        data = {
            'status_report_frequency': 'monthly',
            'overtime_policy': 'optional',
            'company_id': self.company.id,
        }
        logger.info(f"DecisionMakingTestCase.test_decision_making_view posting to {url} with data: {data}")
        response = self.client.post(url, data)
        
        # Check that the view redirects after successful form submission
        # It's complaining about hitting /game instead of /game/game, but
        # seems to be working fine, so ignoring this part.
        self.assertRedirects(response, reverse('game_loop'))
        
        # Refresh employee from database
        self.employee.refresh_from_db()
        
        # Check that employee attributes have not been updated (applied in game loop)
        self.assertEqual(self.employee.morale, 75)
        self.assertEqual(self.employee.productivity, 75)
