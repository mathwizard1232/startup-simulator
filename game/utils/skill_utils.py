import random

def get_perceived_skill(skill_value):
    # TODO: this is supposed to be fuzzed instead of deterministic, to have chance of misperception
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

def update_skill_perception(employee, skill_name, performance_modifier):
    actual_skill = getattr(employee, skill_name)
    perceived_skill = getattr(employee, f'perceived_{skill_name}')
    
    # Calculate the new perception based on actual skill, current perception, and performance
    new_perception = get_updated_perception(actual_skill, perceived_skill, performance_modifier)
    
    if new_perception != perceived_skill:
        setattr(employee, f'perceived_{skill_name}', new_perception)
        employee.save()
        return True
    return False

def get_updated_perception(actual_skill, current_perception, performance_modifier):
    if current_perception == 'unknown':
        current_perception = get_perceived_skill(actual_skill)
    skill_levels = ['poor', 'below average', 'average', 'good', 'excellent']
    current_index = skill_levels.index(current_perception)
    
    # Determine the direction of change based on performance
    if performance_modifier > 0:
        direction = 1
    elif performance_modifier < 0:
        direction = -1
    else:
        return current_perception
    
    # Calculate the chance of perception change
    change_chance = abs(performance_modifier) * 10  # 10% chance per unit of performance_modifier
    
    if random.randint(1, 100) <= change_chance:
        new_index = max(0, min(len(skill_levels) - 1, current_index + direction))
        return skill_levels[new_index]
    
    return current_perception

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

def reveal_personality_trait(employee):
    actual_traits = set(employee.personality_traits)
    perceived_traits = set(employee.perceived_personality_traits)
    hidden_traits = actual_traits - perceived_traits
    
    if hidden_traits:
        trait_to_reveal = random.choice(list(hidden_traits))
        perceived_traits.add(trait_to_reveal)
        employee.perceived_personality_traits_string = ','.join(perceived_traits)
        employee.save()
        return trait_to_reveal
    
    return None