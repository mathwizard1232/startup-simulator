from django.shortcuts import redirect
from ..models.company import Company
from ..models.bug import Bug
import random
import logging

logger = logging.getLogger(__name__)

def get_company_or_redirect(request):
    """
    Retrieves the company for the current session or redirects to start_game.
    
    Args:
    request: The HTTP request object.
    
    Returns:
    A tuple (Company, HttpResponseRedirect). If a company is found, the second element is None.
    If no company is found, the first element is None and the second is a redirect response.
    """
    # Take company_id from session, if not there, take it from the form post.
    # This is primarily needed for testing, where we're posting form data directly
    # rather than going through the usual channels.
    # TODO: eventually this may be a security concern; think about this before production use
    company_id = request.session.get('company_id') or request.POST.get('company_id')
    logger.info(f"get_company_or_redirect called with company_id: {company_id}")
    if not company_id:
        logger.info("get_company_or_redirect redirecting to start_game")
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

def fix_detected_bugs(project, progress_chance):
    """
    Attempts to fix detected bugs in a project.
    
    Args:
    project: The Project instance.
    progress_chance: The probability of fixing a bug (0-100).
    
    Returns:
    int: The number of bugs fixed.
    
    TODO: Implement a system to keep a record of fixed bugs on a given project.
    """
    bugs_fixed = 0
    for bug in Bug.objects.filter(feature__project=project, state='DETECTED'):
        if random.randint(1, 100) <= progress_chance:
            generate_random_bug(bug.project, bug.feature, 100 - progress_chance)
            bug.delete()
            bugs_fixed += 1
    return bugs_fixed

def progress_feature(feature, progress_chance, bug_chance, debugging_chance):
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
        
        feature.save()
        
        if feature.state != initial_state:
            progress = 1
    
    return progress, bugs
