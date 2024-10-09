# Startup Simulator - Technical Details

## Game Structure
- Turn-based gameplay
- Variable turn lengths:
  - Basic scenarios: 1 month per turn
  - Intermediate scenarios: 1 week per turn
  - Advanced scenarios: 1 day per turn (e.g., engineering manager in a F100 company or startup CEO with a team of 25 using AI acceleration)

## Core Mechanics
- Resource management (money, employees, product development)
- Strategic decision-making
- Code/bug/feature management
- All decisions impact code quality to some degree

## User Interface
- Web-based application
- Responsive design for all devices
- Simple and straightforward HTML/CSS/JavaScript
- Accessibility considerations:
  - Avoid text embedded in images
  - Screen reader-friendly layout
- Internationalization/localization planned for future (not in demo or MVP scope)

## Data Storage
- Database-backed persistence
- Hosted version: 
  - Hosted database as source of truth
  - Clients connect over public internet
- Local version: 
  - Local database (e.g., SQLite)
  - Player connects on localhost
- Code remains largely unaffected, differences mainly in configuration

## Technology Stack
- Backend: Python/Django
- Frontend: Plain HTML/CSS/JavaScript
- Database: 
  - Local version: SQLite
  - Hosted version: PostgreSQL (or similar)

## Minimum Viable Product (MVP)
- Refer to implementation guide for specific features in demo vs MVP vs future roadmap

## Scalability
- Not a concern for the demo version

## Randomization
- Core element of randomness for "fog of war" effect
- Allows for risk-taking with uncertain outcomes
- Examples:
  - Pushing an employee harder may result in improved performance or resignation
  - Outcomes not 100% predictable
  - Choices influence probabilities (e.g., happy employees more likely to stay)

## Development Approach
- Prioritize core gameplay mechanics over visual polish in early phases
- Maintain flexibility to adjust features based on playtesting feedback
- Balance realism with engaging gameplay
- Incorporate educational elements naturally through gameplay, avoiding explicit tutorials

## Testing Strategy
- Implement basic tests after each feature to prevent regressions
- Specific testing strategy to be decided as development progresses

## Deployment
- Web-based application
- Consider standalone version for future development

## Decimal Usage
- Always use `decimal.Decimal` for financial calculations to avoid floating-point precision issues.
- Import Decimal at the top of files where it's used: `from decimal import Decimal`
- Convert integer or string values to Decimal when performing calculations: `Decimal('10000')` or `Decimal(integer_value)`
- Avoid using float values in financial calculations.