import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import random

class StartupSimulatorTest(StaticLiveServerTestCase):
    def setUp(self):
        # Configure ChromeOptions
        options = webdriver.ChromeOptions()
        # Uncomment the below line to run tests in headless mode
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')  # Bypass OS security model
        options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

        try:
            self.driver = webdriver.Chrome(options=options)
            print("WebDriver initialized successfully")
        except Exception as e:
            print(f"Failed to initialize WebDriver: {e}")
            raise

        # Initialize WebDriverWait with short timeout
        self.wait = WebDriverWait(self.driver, 2)
        print(f"Driver session ID: {self.driver.session_id}")

    def tearDown(self):
        self.driver.quit()
        print("WebDriver quit successfully")

    def take_screenshot(self, name):
        """Utility method to take screenshots on exceptions."""
        timestamp = int(time.time())
        screenshot_name = f'screenshot_{name}_{timestamp}.png'
        self.driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved as {screenshot_name}")

    def test_win_scenario(self):
        try:
            # Start a new game
            self.start_new_game('Test Company', 'Fintech')

            # Play through the game
            for turn in range(200):  # Assume 200 turns to reach win condition by single project
                print(f"Turn {turn + 1}")
                
                # Make decisions only on the first turn
                if turn == 0:
                    self.make_turn_decisions(first_turn=True)
                
                # End the current turn
                self.end_turn()

                # Check for win condition
                if self.check_win_condition():
                    print("Win condition met")
                    break

            # Assert that the win condition was reached
            self.assertTrue(
                self.check_win_condition(), "Win condition was not reached"
            )
            print("Win scenario test passed successfully")
        except Exception as e:
            self.take_screenshot('test_win_scenario_error')
            print(f"Error in test_win_scenario: {e}")
            raise

    def test_lose_scenario(self):
        try:
            # Start a new game
            self.start_new_game('Test Company', 'Fintech')

            # Hire employees until we can't afford more
            self.hire_employees_until_broke()

            # Advance turns until we lose or reach a maximum number of turns
            max_turns = 50
            for turn in range(max_turns):
                print(f"Turn {turn + 1}")
                self.end_turn()

                # Check for lose condition
                if self.check_lose_condition():
                    print("Lose condition met")
                    break

            # Assert that the lose condition was reached
            self.assertTrue(
                self.check_lose_condition(), "Lose condition was not reached"
            )
            print("Lose scenario test passed successfully")
        except Exception as e:
            self.take_screenshot('test_lose_scenario_error')
            print(f"Error in test_lose_scenario: {e}")
            raise

    def make_turn_decisions(self, first_turn=False):
        """Implement decision-making logic for each turn."""
        try:
            if first_turn:
                # Hire an employee
                self.hire_employee()

                # Create a project
                self.create_project()

                # Assign employee to project
                self.assign_employee_to_project()
            else:
                # For non-first turns, we don't need to do anything
                pass
        except Exception as e:
            print(f"Error in make_turn_decisions: {e}")
            self.take_screenshot('make_turn_decisions_error')

    def hire_employee(self):
        hire_button = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Hire New Employee'))
        )
        hire_button.click()
        print("Clicked hire button")

        self.wait.until(EC.presence_of_element_located((By.ID, 'fast_worker')))
        print("Hire page loaded")

        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        submit_button.click()
        print("Submitted hire form")

        self.wait.until(EC.url_contains('/game/game/'))
        print("Redirected back to game loop after hiring")

    def create_project(self):
        start_project_button = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Create New Project'))
        )
        start_project_button.click()
        print("Clicked create project button")

        self.wait.until(EC.presence_of_element_located((By.ID, 'project_name')))
        print("Create project page loaded")

        project_name = self.driver.find_element(By.ID, 'project_name')
        project_name.send_keys(f"Project {random.randint(1, 1000)}")
        project_description = self.driver.find_element(By.ID, 'project_description')
        project_description.send_keys("This is a test project description.")

        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        submit_button.click()
        print("Submitted create project form")

        self.wait.until(EC.url_contains('/game/game/'))
        print("Redirected back to game loop after project creation")

    def assign_employee_to_project(self):
        manage_project_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Manage'))
        )
        manage_project_link.click()
        print("Clicked manage project link")

        assign_employees_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Assign Employees'))
        )
        assign_employees_link.click()
        print("Clicked assign employees link")

        employee_checkbox = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"]'))
        )
        employee_checkbox.click()
        print("Selected employee")

        assign_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        assign_button.click()
        print("Submitted assign employees form")

        self.driver.get(f'{self.live_server_url}/game/game/')
        print("Manually navigated back to game loop page")

    def check_win_condition(self):
        """Check if the win condition is met based on company funds."""
        try:
            funds_element = self.driver.find_element(
                By.XPATH, "//p[contains(text(), 'Funds:')]"
            )
            funds_text = funds_element.text
            funds = float(funds_text.split('$')[1].replace(',', ''))
            print(f"Current funds: {funds}")
            return funds >= 1000000
        except Exception as e:
            print(f"Error checking win condition: {e}")
            self.take_screenshot('check_win_condition_error')
            return False

    def check_lose_condition(self):
        """Check if the lose condition is met based on company funds."""
        try:
            funds_element = self.driver.find_element(
                By.XPATH, "//p[contains(text(), 'Funds:')]"
            )
            funds_text = funds_element.text
            funds = float(funds_text.split('$')[1].replace(',', ''))
            print(f"Current funds: {funds}")
            return funds <= 0
        except Exception as e:
            print(f"Error checking lose condition: {e}")
            self.take_screenshot('check_lose_condition_error')
            return False

    def start_new_game(self, company_name="Test Company", industry="Fintech"):
        self.driver.get(f'{self.live_server_url}/game/')
        print("Navigated to start page")
        print(f"Current URL: {self.driver.current_url}")

        company_name_field = self.wait.until(
            EC.presence_of_element_located((By.ID, 'company_name'))
        )
        company_name_field.send_keys(company_name)
        print("Entered company name")

        industry_select = self.wait.until(
            EC.presence_of_element_located((By.ID, 'industry'))
        )
        Select(industry_select).select_by_visible_text(industry)
        print("Selected industry")

        start_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        start_button.click()
        print("Clicked start button")

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//h1[contains(text(), '{company_name}')]")
            )
        )
        print("Game loop page loaded successfully")

    def end_turn(self):
        end_turn_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        print("Found end turn button")
        end_turn_button.click()
        print("Clicked end turn button")

    def hire_employees_until_broke(self):
        while True:
            try:
                self.hire_employee()
            except Exception as e:
                print(f"No more employees can be hired or an error occurred during hiring: {e}")
                # Navigate back to the game loop page
                self.driver.get(f'{self.live_server_url}/game/game/')
                print("Returned to game loop after hiring attempt failed")
                break  # Break the loop if we can't hire more employees

if __name__ == '__main__':
    unittest.main()