from django.shortcuts import redirect
from .models.company import Company
from .models.bug import Bug
import random

def get_company_or_redirect(request):
    """
    Retrieves the company for the current session or redirects to start_game.
    
    Args:
    request: The HTTP request object.
    
    Returns:
    A tuple (Company, HttpResponseRedirect). If a company is found, the second element is None.
    If no company is found, the first element is None and the second is a redirect response.
    """
    company_id = request.session.get('company_id')
    if not company_id:
        return None, redirect('start_game')
    return Company.objects.get(id=company_id), None

def generate_random_bug(project, feature, bug_chance):
    """
    Generates a random bug based on the given bug chance.
    
    Args:
    project: The Project instance.
    feature: The Feature instance.
    bug_chance: The probability of generating a bug (0-100).
    
    Returns:
    None
    """
    if random.randint(1, 100) <= bug_chance:
        Bug.objects.create(
            project=project,
            feature=feature,
            description="Randomly generated bug",
            state='UNDETECTED'
        )

def progress_feature(feature, progress_chance):
    """
    Progresses a feature's state based on the given progress chance.
    
    Args:
    feature: The Feature instance.
    progress_chance: The probability of progressing the feature (0-100).
    
    Returns:
    None
    """
    if random.randint(1, 100) <= progress_chance:
        if feature.state == 'NOT_STARTED':
            feature.state = 'IN_PROGRESS'
        elif feature.state == 'IN_PROGRESS':
            feature.state = 'TESTING'
        elif feature.state == 'TESTING':
            # Chance to detect existing bugs
            for bug in feature.bugs.filter(state='UNDETECTED'):
                if random.randint(1, 100) <= progress_chance:
                    bug.state = 'DETECTED'
                    bug.save()
            
            if not feature.bugs.filter(state='DETECTED').exists():
                feature.state = 'COMPLETED'
        feature.save()

def fix_detected_bugs(project, progress_chance):
    """
    Attempts to fix detected bugs in a project.
    
    Args:
    project: The Project instance.
    progress_chance: The probability of fixing a bug (0-100).
    
    Returns:
    None
    
    TODO: Implement a system to keep a record of fixed bugs on a given project.
    """
    for bug in Bug.objects.filter(feature__project=project, state='DETECTED'):
        if random.randint(1, 100) <= progress_chance:
            generate_random_bug(bug.project, bug.feature, 100 - progress_chance)
            bug.delete()
