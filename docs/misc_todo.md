Various notes that aren't in other docs yet. Append for writes. Remove when added to other docs.

- TODO: diminishing returns when combining employees, scaled by teamwork
  - Especially bad if number of teammates exceeds number of features
- TODO: automatically assign unassigned employees to projects on easy mode?
- TODO: automatically assign employees to features if they are on a project (allow manual override)
- Add a `completed` boolean field to the `Project` model for more efficient querying of completed projects. Update this field in the `process_project` method when all features are completed.
- Add a `completed` boolean field to the `Feature` model for more efficient querying of completed features. Update this field in the `process_feature` method when a feature is completed.
- Have an employee assigned to a particular feature if they are on the project.
- Update calculations for progress based on skill of employees and how many other employees are on the
same project and/or feature. Employees on the same project will interfere slightly; employees on the same feature will interfere more (this is presuming that all employees are programmers; later on there will be other types of employees who will interfere less or more depending on their role).
- Add an automatic code formatter like `black` to the project.
- After a long time jump, show a summary of events that happened while the player was away (and project progress).
- Refine `update_skill_perception` logic per notes there.
- Fix decision making so it's not just instant application of effects.
- Fix decision making (morale and productivity had gotten removed in a different change and broke it)
- Fix `get_company_or_redirect` so that there's not a security vulnerability being able to just set company_id in the POST request to switch companies. (Fix before production use.)
