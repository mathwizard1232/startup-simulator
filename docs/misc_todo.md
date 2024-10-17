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
- Eventually have gradual reveal of personality traits?
- use a fixed seed for testing the game to avoid randomness in test outcomes
- We need to eventually have a realistic customer / contract aspect which will give us feedback mechanisms for the features and quality in terms of whether the player can sell the software or not.
- We need to have competitor companies who can beat the player to market. There should be a realistic first mover advantage, while the "second mover" needs to be able to beat the first-to-market in terms of features and quality (or in better sales, but that's not so much the focus of this game)

Possibly (AI suggested, good enough to save but not certain if / when we'll do all of it):
- Have an "assignment" screen that shows the player's current employees and allows them to be reassigned to different projects.
- Have a "firing" screen that shows the player's current employees and allows them to be fired.
- Have a "training" screen that shows the player's current employees and allows them to be trained.
- Have a "promotion" screen that shows the player's current employees and allows them to be promoted.
- Have a "demotion" screen that shows the player's current employees and allows them to be demoted.
- Have a "transfer" screen that shows the player's current employees and allows them to be transferred to other projects.
