import random

first_names = [
    "Byte", "Pixel", "Glitch", "Data", "Chip", "Net",
    "John", "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia",
    "Wei", "Yuki", "Raj", "Zara", "Chen", "Aisha", "Hiroshi", "Fatima"
]

last_names = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Lee", "Wong", "Kim", "Nguyen", "Patel", "Singh", "Chen", "Yang", "Wu", "Liu",
    "Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"
]

nicknames = [
    "Bug", "Crash", "Hack", "Code", "Logic", "Algo", "Nano", "Quantum", "Vector", "Syntax", "Binary", "Cache",
    "Quirky", "Nerdy", "Sleepy", "Caffeinated", "Eccentric", "Meticulous", "Chaotic", "Innovative", "Distracted", "Focused"
]

def generate_name():
    first = random.choice(first_names)
    last = random.choice(last_names)
    nickname = random.choice(nicknames)
    return f"{first} '{nickname}' {last}"
