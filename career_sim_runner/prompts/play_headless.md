## Current task
Start a new Career Survival Agent game. Play according to the rules in IDENTITY.md and the installed skills.

### Recommended first steps
1. Call `show_employee_handbook` once to learn the rules.
2. Call `new_game` and print `SESSION_ID=<session_id>`.
3. Then loop with the core rules: `observe` → decide → `take_action` until the game ends.
4. When the game ends, print the full `ending_score` payload, then output `DONE`.
