import random

def update_skill_perception(employee, skill_name, performance_modifier):
    # TODO: make this logic more sensible
    # Right now, the performance modifier affects the chance of updating,
    # but not the direction. Instead, it should push the perception in that
    # direction, but not necessarily make it more likely.
    # Probably pass through performance_modifier to `get_perceived_skill`,
    # and then have the performance affect the perception.
    # Also, we probably want to send in the current perceived skill.
    # So get_perceived_skill should be a function of the actual skill,
    # the current perception, and whether the event is positive or negative.
    actual_skill = getattr(employee, skill_name)
    perceived_skill = getattr(employee, f'perceived_{skill_name}')
    
    # Chance to update perception based on performance
    if random.random() < 0.3 + (performance_modifier * 0.1):
        new_perception = employee.get_perceived_skill(actual_skill)
        if new_perception != perceived_skill:
            setattr(employee, f'perceived_{skill_name}', new_perception)
            employee.save()
            return True
    return False

def update_employee_perceptions(employee, project_success, bug_count, teamwork_rating):
    updates = []
    
    # Update coding speed and accuracy perceptions
    if update_skill_perception(employee, 'coding_speed', project_success):
        updates.append('coding speed')
    if update_skill_perception(employee, 'coding_accuracy', -bug_count):
        updates.append('coding accuracy')
    
    # Update debugging perception
    if bug_count > 0 and update_skill_perception(employee, 'debugging', -bug_count):
        updates.append('debugging')
    
    # Update teamwork perception
    if update_skill_perception(employee, 'teamwork', teamwork_rating):
        updates.append('teamwork')
    
    return updates