# planned_tasks

One task per file: `pt-web-app-dev-expert-<slug>.json`.

- Fields: `id`, `skill`, `title`, `due` (local ISO), `status`
  (pending/running/done/paused/failed), `action`, `session_chain`.
- Due tasks are executed by the SMS scheduler, never by this skill itself.
- Deleting the file unregisters the task. See `template.json`.
