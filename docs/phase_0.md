# Phase 0: Playable Demo Implementation Plan

## Overview
This plan outlines the steps to create a basic playable version of Startup Simulator, implementing core gameplay mechanics and establishing the foundation for future development.

## Steps

1. Set up Django project structure
   - Create a new Django project
   - Set up a new Django app for the game

2. Create basic data models
   - Implement Employee model
   - Implement Project model
   - Implement Company model

3. Implement core game loop
   - Create a view for starting a new game
   - Implement basic turn structure

4. Develop employee management
   - Create a view for hiring employees
   - Implement logic for choosing between perfectionist and fast worker

5. Implement project management
   - Create a view for creating and managing software projects
   - Implement hidden bug generation

6. Develop decision-making mechanics
   - Implement micromanagement options (e.g., frequency of status reports)
   - Create a view for making decisions

7. Create a simple UI
   - Develop basic HTML templates for game interface
   - Implement minimal CSS for readability

8. Implement two industries
   - Add industry selection to game start
   - Implement basic differences between Fintech and Game Development

9. Create end game conditions
   - Implement basic win/lose scenarios
   - Create an end game screen

9.5. Refactor turn-based gameplay
   - Connect "end turn" action to project progress
   - Implement logical salary deduction per turn
   - Remove manual project update button
   - Ensure turn counter advances correctly

10. Implement resource allocation and revenue generation
    - Create a view for assigning developers to projects
    - Implement basic resource management logic
    - Add simple revenue generation mechanics (e.g., completed projects generate income)
    - Balance income and expenses to make the game winnable

11. Develop basic result visualization
    - Create a simple dashboard for viewing game progress
    - Implement basic charts or graphs for key metrics

12. Polish and bug fixing
    - Playtest the game
    - Fix any critical bugs or issues

Note on testing: Consider implementing basic tests after each feature to prevent regressions. The specific testing strategy can be decided as development progresses.

## Conclusion
By following these steps, we aim to create a basic playable version of Startup Simulator that implements the core gameplay mechanics and establishes a foundation for future development.
