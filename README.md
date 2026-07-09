# Task Tracker Demo Python

This is a small command-line task tracker used for Codex subagent demonstrations.

The program runs locally and does not require a server, network access, or third-party packages.

## Run The App

```bash
python app.py
```

Task data is stored in `tasks.json` beside `app.py`, regardless of the directory from which the command is run.

## Run The Tests

```bash
python -m unittest discover -s tests -v
```

## Suggested Manual Test

Use the menu in this order:

1. Add task: `Buy milk`
2. Add task: `Write report`
3. List tasks (option `2`); expect both `#1` and `#2` to be open.
4. Complete task `#2` (option `3`); expect a completed message.
5. Show stats (option `4`); expect total 2, open 1, completed 1.
6. List tasks again; expect `#1` open and `#2` done.
7. Save and exit (option `5`).
8. Run `python app.py` again and list tasks; expect the same tasks and statuses.

## Expected Behavior

- Adding two tasks should create two different task IDs.
- Completing task id `2` should complete the second task.
- Saving and restarting should keep the task list.
- Completed and open task counts should match the visible list.

## Storage And Recovery

New saves use the canonical JSON object format `{"tasks": [...]}`. For compatibility, the loader also accepts the legacy bare-list format. Data is validated before it is loaded or replaced. If `tasks.json` is malformed or has invalid task fields, the app reports its full path and exits without overwriting it. Move the damaged file aside or repair its JSON before restarting.

Option `5` saves and exits. If saving fails, the app stays open with changes in memory so saving can be retried. Option `6` does not save and asks for confirmation when changes are pending. Ctrl+C or end-of-input exits cleanly without writing unsaved changes.

## Project Areas

Use Codex subagents to inspect the project from multiple angles:

- CLI workflow behavior
- task state management
- file persistence
- tests and documentation consistency
