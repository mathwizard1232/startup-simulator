# Startup Simulator

Startup Simulator is a game where you can simulate the growth of your startup. 
You can choose from a variety of industries, and then you can choose from a variety of actions to take. 
The game will then simulate the growth of your startup, and you can watch as your startup grows and evolves.

## Technologies Used

Python/Django base, written using Cursor with Claude 3.5 Sonnet.

## How to Play

1. Clone the repository
2. Run `pip install -r requirements.txt`
3. Run `python manage.py runserver`
4. Go to `http://localhost:8000` in your web browser


## Status

This game is currently at a "playable demo" state at the time of initial upload.

While it's possible to run and get to the win condition, the game is only technically
playable, not yet truly a demonstration of the concept in the sense of an enjoyable
and complex game.

So feel free to run it, but know that this is just a rough demonstration of the core concept.

Of more initial interest might be the design documents which covers a lot of the ideas
for future development.

I'm currently working on refactoring the code in preparation for the next phase of development. Feel
free to run latest or to check out the latest tag to see the demo in a working version if latest is broken. I've been bumping patch versions so far but when I complete the MVP I'll give it at least a minor version bump.

## Project Structure

The project follows a standard Django structure with some custom organization:

```
startup_simulator/
│
├── game/
│ ├── models/
│ │ ├── employee.py
│ │ ├── project.py
│ │ ├── company.py
│ │ └── ...
│ ├── views/
│ │ ├── employee_views.py
│ │ ├── project_views.py
│ │ ├── game_views.py
│ │ ├── decision_views.py
│ │ └── ...
│ ├── forms/
│ │ ├── employee_form.py
│ │ ├── project_form.py
│ │ ├── decision_form.py
│ │ └── ...
│ ├── templates/
│ │ └── game/
│ │ ├── base.html
│ │ ├── start_game.html
│ │ ├── game_loop.html
│ │ └── ...
│ ├── static/
│ │ ├── css/
│ │ ├── js/
│ │ └── images/
│ ├── utils.py
│ ├── urls.py
│ └── apps.py
│
├── startup_simulator/
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── docs/
│ ├── DESIGN.md
│ ├── IMPLEMENTATION.md
│ ├── FUTURE_IMPROVEMENTS.md
│ └── ...
│
├── manage.py
└── README.md
```

## Key Components

- `models/`: Data models for the game (Employee, Project, Company, etc.)
- `views/`: View logic, separated into different files for better organization
- `forms/`: Form classes for handling user input
- `templates/`: HTML templates for rendering the game interface
- `static/`: Static files (CSS, JavaScript, images)
- `utils.py`: Utility functions used across the application
- `urls.py`: URL patterns for the game app
- `docs/`: Documentation files for design, implementation, and future improvements

## Features

- Employee management (hiring, assigning to projects)
- Project management (creation, development, bug generation)
- Financial management (budget allocation, revenue tracking)
- Industry-specific mechanics (Fintech and Game Development)
- Decision-making system (micromanagement options)
- Turn-based gameplay

## Setup and Running the Game

1. Clone the repository
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start the development server: `python manage.py runserver`
5. Access the game at `http://localhost:8000`

## Development

- Development is about to start on the MVP (Minimum Viable Product) phase
- Refer to `docs/IMPLEMENTATION.md` for the current development plan
- Future improvements and features are outlined in `docs/FUTURE_IMPROVEMENTS.md`

## Testing

- End-to-end tests are implemented using Selenium with Python
- Refer to `docs/TEST_PLAN.md` for the testing strategy and implementation details

## Contributing

We welcome contributions to Startup Simulator! Please refer to our contributing guidelines (TODO: create CONTRIBUTING.md) for more information on how to get involved. The biggest thing you can do right now is to play the game and provide feedback!

## License

I will eventually add a license. For now, you may run the code, copy it, and modify it, but you may not sell it nor claim it as your own. This will likely eventually be a creative commons attribution-noncommercial-sharealike license, but for now it's just a "do whatever you want with it but give me credit and don't make money without making a deal with me first" guideline and contact me if you want to make a deal.