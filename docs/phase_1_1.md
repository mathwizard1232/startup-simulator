# Phase 1.1: Refactor Turn Structure

## Overview
This document outlines the implementation plan for refactoring the turn structure in Startup Simulator. The goal is to implement variable turn lengths (day, week, month) while maintaining consistency in game outcomes regardless of the chosen time increment.

## Implementation Steps

1. Update Game Model
   - Add a field to track the current game date
   - Implement methods to advance time by day, week, and month

2. Refactor Core Game Loop
   - Modify the main game loop to process events on a daily basis
   - Implement a system to handle player absence for longer periods

3. Create Turn Selection Interface
   - Design and implement a UI for selecting turn length
   - Options: "Call it a day", "Take a week off", "Go fishing for a month"

4. Implement Time-Based Event System
   - Create a queue for scheduled events
   - Develop a system to process events that occur during player absence

5. Adjust Resource Calculations
   - Modify salary calculations to prorate based on time passed
   - Update project progress calculations to account for variable time increments

6. Implement Player Absence Logic
   - Create a system to simulate "no-action" decisions for events during absence
   - Implement different consequences for being absent vs. ignoring events while present

7. Update UI to Reflect Time Passage
   - Modify the game interface to clearly show the current date
   - Implement a system to summarize events and changes during longer time jumps

8. Balancing and Testing
   - Conduct thorough testing to ensure consistency across different time increments
   - Balance event frequency and impact for different turn lengths

## Detailed Implementation Notes

### 1. Update Game Model
- Add a `current_date` field to the Game model
- Implement `advance_time(days)` method to progress the game date

### 2. Refactor Core Game Loop
- Modify the main game loop to call `advance_time(1)` for each day
- Implement logic to process multiple days when player chooses week or month options

### 3. Create Turn Selection Interface
- Design a user-friendly interface for selecting turn length
- Implement logic to trigger appropriate time advancement based on selection

### 4. Implement Time-Based Event System
- Create an Event model with fields for date, type, and details
- Implement a system to generate and queue events
- Develop logic to process queued events when advancing time

### 5. Adjust Resource Calculations
- Modify salary deduction to occur daily instead of per turn
- Update project progress to accumulate daily based on assigned resources

### 6. Implement Player Absence Logic
- Create a flag to indicate player absence
- Implement default decision-making logic for events during absence
- Develop a system to summarize missed events and their outcomes

### 7. Update UI to Reflect Time Passage
- Add a prominent display of the current game date
- Implement a summary view for longer time jumps, showing key events and changes

### 8. Balancing and Testing
- Develop automated tests to verify consistency across different time increments
- Create scenarios to test various combinations of events and time jumps
- Adjust event frequency and impact to maintain game balance for all turn lengths

## Considerations
- Ensure that advancing time day-by-day produces the same outcome as taking larger jumps, assuming no player intervention
- Design the system to be flexible for potential future additions (e.g., year-long or decade-long jumps)
- Consider implementing a configuration option to disable events for playthroughs where players want to advance time freely without penalties

## Testing Strategy
- Implement unit tests for time advancement and event processing functions
- Create integration tests to verify consistency of game state across different time increments
- Conduct manual playtesting to ensure the new turn structure feels intuitive and engaging

## UI/UX Considerations
- Design the turn selection interface to clearly communicate the implications of each option
- Provide clear feedback to the player about events and changes that occurred during longer time jumps
- Consider adding tooltips or help text to explain the pros and cons of different turn length choices

By implementing these changes, we'll create a flexible and engaging turn structure that allows players to choose their level of involvement while maintaining consistent and realistic game progression.