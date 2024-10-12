Various notes that aren't in other docs yet. Append for writes. Remove when added to other docs.

- TODO: diminishing returns when combining employees, scaled by teamwork
  - Especially bad if number of teammates exceeds number of features
- TODO: automatically assign unassigned employees to projects on easy mode?
- TODO: automatically assign employees to features if they are on a project (allow manual override)
- Add a `completed` boolean field to the `Project` model for more efficient querying of completed projects. Update this field in the `process_project` method when all features are completed.