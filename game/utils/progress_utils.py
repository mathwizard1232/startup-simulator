import logging
from decimal import Decimal
from django.contrib import messages
from .skill_utils import update_employee_perceptions, reveal_personality_trait
from .utils import generate_random_bug, fix_detected_bugs
import random

logger = logging.getLogger(__name__)

def progress_feature_internal(feature, progress_chance, bug_chance, debugging_chance):
    """
    Progresses a feature's state based on the given progress chance.
    
    Args:
    feature: The Feature instance.
    progress_chance: The probability of progressing the feature (0-100).
    
    Returns:
    tuple: (progress, bugs)
    """
    progress = 0
    bugs = 0

    if feature.state == 'IN_PROGRESS':
        # Generate new bugs potentially while building
        generate_random_bug(feature.project, feature, bug_chance)
    
    if random.randint(1, 100) <= progress_chance:
        initial_state = feature.state
        if feature.state == 'NOT_STARTED':
            feature.state = 'IN_PROGRESS'
        elif feature.state == 'IN_PROGRESS':
            feature.state = 'TESTING'
        elif feature.state == 'TESTING':
            # First try to fix detected bugs
            bugs -= fix_detected_bugs(feature.project, debugging_chance)

            # Chance to detect existing bugs
            for bug in feature.bugs.filter(state='UNDETECTED'):
                if random.randint(1, 100) <= debugging_chance:
                    bug.state = 'DETECTED'
                    bug.save()
                    # Only count bugs that were detected
                    bugs += 1
            
            # If no bugs are detected, we'll call testing done
            if not feature.bugs.filter(state='DETECTED').exists():
                feature.state = 'COMPLETED'
                # When completing a project, reveal a hidden trait, if any, for each employee
                for employee in feature.project.employees.all():
                    reveal_personality_trait(employee)
        
        feature.save()
        
        if feature.state != initial_state:
            progress = 1
    
    return progress, bugs

def process_project(request, project):
    company = project.company
    employees = project.employees.all()
    features = project.features.filter(state__in=['NOT_STARTED', 'IN_PROGRESS', 'TESTING'])

    if not features:
        return

    feature_speed = {}
    feature_accuracy = {}
    feature_debugging = {}
    feature_productivity = {}
    feature_teamwork = {}
    feature_traits = {}
    remaining_employees = list(employees)
    deadline_modifier = get_deadline_modifier(project.deadline_type)

    # Apply micromanagement effects
    status_report_modifier = get_status_report_modifier(company.status_report_frequency)
    overtime_modifier = get_overtime_modifier(company.overtime_policy)

    # Assign employees to features
    for feature in features:
        if not remaining_employees:
            break
        employee = remaining_employees.pop(0)
        logger.info(f"Assigning employee {employee.name} with {employee.personality_traits} and {employee.coding_speed}, {employee.coding_accuracy}, {employee.debugging}, {employee.teamwork} to feature {feature.name}")
        
        feature_speed[feature] = employee.coding_speed * status_report_modifier['speed'] * overtime_modifier['speed']
        feature_accuracy[feature] = employee.coding_accuracy * status_report_modifier['accuracy'] * overtime_modifier['accuracy']
        feature_debugging[feature] = employee.debugging * status_report_modifier['debugging'] * overtime_modifier['debugging']
        feature_teamwork[feature] = employee.teamwork * deadline_modifier['teamwork'] * status_report_modifier['teamwork'] * overtime_modifier['teamwork']
        feature_productivity[feature] = employee.productivity * status_report_modifier['productivity'] * overtime_modifier['productivity']
        feature_traits[feature] = employee.personality_traits

    # Distribute remaining employees
    while remaining_employees:
        for feature in feature_speed:
            if not remaining_employees:
                break
            current_speed = feature_speed[feature]
            current_accuracy = feature_accuracy[feature]
            current_debugging = feature_debugging[feature]
            new_employee = remaining_employees.pop(0)
            additional_speed = new_employee.coding_speed
            additional_accuracy = new_employee.coding_accuracy
            additional_debugging = new_employee.debugging
            # Team's teamwork skill is the highest individual skill
            teamwork = max(feature_teamwork[feature], new_employee.teamwork * deadline_modifier['teamwork'])
            # Speed is the hardest to increase with more people
            # Perfect teamwork allows 25% increase at most
            speed_factor = Decimal(0.25) * Decimal(teamwork) / Decimal(10)
            # Accuracy is easier to increase with more people
            accuracy_factor = Decimal(0.5) * Decimal(teamwork) / Decimal(10)
            debugging_factor = accuracy_factor
            # Cap at 16 skill level - higher than individual but still imperfect
            feature_speed[feature] = max(16, current_speed + speed_factor * additional_speed)
            feature_accuracy[feature] = max(16, current_accuracy + accuracy_factor * additional_accuracy)
            feature_debugging[feature] = max(16, current_debugging + debugging_factor * additional_debugging)
            feature_teamwork[feature] = teamwork
            feature_traits[feature] = feature_traits[feature].append(new_employee.personality_traits)

    total_progress = 0
    total_bugs = 0
    for feature, speed_skill in feature_speed.items():
        if 'meme_lord' in feature_traits[feature]:
            feature_productivity[feature] += 10
        # Apply deadline modifiers
        adjusted_speed = speed_skill * deadline_modifier['speed']
        adjusted_accuracy = feature_accuracy[feature] * deadline_modifier['accuracy']
        adjusted_debugging = feature_debugging[feature] * deadline_modifier['debugging']
        

        # Calculate progress and bug chances (existing code with adjusted values)
        progress_chance = min(adjusted_speed * 7.5 * feature_productivity[feature] / 100, 95)
        bug_chance = max(100 - adjusted_accuracy * 7.5, 5)
        debugging_chance = min(adjusted_debugging * 7.5, 95)

        # Process feature (existing code)
        progress, bugs = process_feature(feature=feature, project=project, 
                                                progress_chance=progress_chance, 
                                                bug_chance=bug_chance, 
                                                debugging_chance=debugging_chance)
        total_progress += progress
        total_bugs += bugs

    # Calculate project success based on progress and bugs
    project_success = total_progress / len(features) - (total_bugs * 0.1)
    
    # Update employee perceptions
    for employee in employees:
        updates = update_employee_perceptions(employee, project_success, total_bugs, len(employees))
        if updates:
            messages.info(request, f"{employee.name}'s perceived {', '.join(updates)} has been updated.")

def process_feature(feature, project, progress_chance, bug_chance, debugging_chance):
    logger.info(f"Processing feature {feature.name} with state {feature.state} and {progress_chance} progress chance, {bug_chance} bug chance, and {debugging_chance} debugging chance")
    if feature.state == 'NOT_STARTED':
        start_feature(feature, project, bug_chance=bug_chance)
        return 1, 0  # We can always start and no bugs are detected
    else:
        return progress_feature_internal(feature=feature, progress_chance=progress_chance, bug_chance=bug_chance, debugging_chance=debugging_chance)

def start_feature(feature, project, bug_chance):
    feature.state = 'IN_PROGRESS'
    generate_random_bug(project, feature, bug_chance)
    feature.save()

def get_deadline_modifier(deadline_type):
    if deadline_type == 'AGGRESSIVE':
        logger.info("Aggressive deadline modifier")
        return {
            'speed': 1.2,
            'accuracy': 0.8,
            'debugging': 0.9,
            'teamwork': 0.9
        }
    elif deadline_type == 'CAUTIOUS':
        logger.info("Cautious deadline modifier")
        return {
            'speed': 0.8,
            'accuracy': 1.2,
            'debugging': 1.2,
            'teamwork': 1.2
        }
    else:  # STANDARD
        logger.info("Standard deadline modifier")
        return {
            'speed': 1.0,
            'accuracy': 1.0,
            'debugging': 1.0,
            'teamwork': 1.0
        }

def get_status_report_modifier(frequency):
    if frequency == 'daily':
        return {
            'speed': 0.9,
            'accuracy': 1.1,
            'debugging': 1.1,
            'teamwork': 0.9,
            'productivity': 0.9
        }
    elif frequency == 'weekly':
        return {
            'speed': 1.0,
            'accuracy': 1.0,
            'debugging': 1.0,
            'teamwork': 1.0,
            'productivity': 1.0
        }
    elif frequency == 'monthly':
        return {
            'speed': 1.1,
            'accuracy': 0.9,
            'debugging': 0.9,
            'teamwork': 1.1,
            'productivity': 1.1
        }

def get_overtime_modifier(policy):
    if policy == 'mandatory':
        return {
            'speed': 1.2,
            'accuracy': 0.8,
            'debugging': 0.9,
            'teamwork': 0.8,
            'productivity': 1.2
        }
    elif policy == 'optional':
        return {
            'speed': 1.1,
            'accuracy': 0.9,
            'debugging': 1.0,
            'teamwork': 0.9,
            'productivity': 1.1
        }
    else:  # no overtime
        return {
            'speed': 1.0,
            'accuracy': 1.0,
            'debugging': 1.0,
            'teamwork': 1.0,
            'productivity': 1.0
        }
