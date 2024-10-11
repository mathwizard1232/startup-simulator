# Phase 1.9: Refine End Game Conditions

## Overview
This document outlines the implementation plan for refining end game conditions in Startup Simulator. The goal is to create more nuanced win and lose conditions that reflect the complexities of running a startup, while also implementing a scenario-based campaign mode.

## Implementation Steps

1. Implement Company Valuation System
   - Create a function to calculate company valuation based on:
     a. 40x revenue from the last three months (annualized)
     b. Current cash balance
   - Set company valuation as the larger of the two calculations

2. Develop Win Conditions
   - Implement a "million-dollar company" win condition based on valuation
   - Create a framework for scenario-specific win conditions (e.g., time-based goals)

3. Implement Lose Conditions
   - Create a system to track company ownership percentage
   - Implement a "loss of control" condition when player ownership falls below 50%
   - For Fintech: Implement a "corporate death penalty" for severe compliance violations
   - Design a system to track and evaluate the severity of bugs and compliance issues

4. Create Scenario Framework
   - Develop a system for defining and loading different scenarios
   - Implement industry-specific scenario locks (Fintech or Game Development)
   - Create a campaign mode with a sequence of scenarios

5. Implement Difficulty Modifiers
   - Design a system of modifiers that affect gameplay based on difficulty level
   - Ensure win/lose conditions remain consistent across difficulty levels

6. Develop End Game Summary
   - Create a system to log notable events during gameplay
   - Design an end game screen to display detailed performance metrics
   - Implement a summary generator to highlight key decisions and their impacts

7. Integrate with Existing Systems
   - Connect end game conditions to the main game loop
   - Implement checks for win/lose conditions at appropriate intervals

## Detailed Implementation Notes

### Company Valuation Calculation
- Implement a rolling 3-month revenue tracker
- Create a function to annualize the 3-month revenue and multiply by 40
- Compare this value with the current cash balance and use the larger value

### Scenario System
- Design a data structure to define scenarios (win conditions, time limits, industry locks)
- Implement a scenario loader and validator
- Create a campaign progression system to unlock scenarios sequentially

### Difficulty Modifiers
- Implement modifiers for various game aspects (e.g., bug frequency, customer acquisition rate)
- Create a system to apply these modifiers based on the chosen difficulty level

### End Game Summary
- Design a data structure to store notable events during gameplay
- Implement a system to evaluate and categorize player decisions and their impacts
- Create a summary generator that compiles this data into a readable format

## Testing Strategy
- Implement unit tests for valuation calculations and win/lose condition checks
- Create integration tests for the scenario system and campaign mode
- Conduct playtesting to ensure balance across different scenarios and difficulty levels

## UI/UX Considerations
- Design an intuitive interface for selecting scenarios and difficulty levels
- Create clear visualizations for company valuation and ownership percentages
- Implement an engaging and informative end game summary screen

By implementing these refined end game conditions and the scenario-based campaign mode, we'll create a more engaging and replayable experience that better reflects the complexities of managing a startup. This system will provide a solid foundation for future expansions and additional scenarios.