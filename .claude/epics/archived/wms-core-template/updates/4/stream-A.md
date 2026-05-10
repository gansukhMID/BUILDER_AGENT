---
issue: 4
stream: implementation
started: 2026-05-08T06:31:33Z
status: in_progress
---
## Scope
db.py — add engine_factory, get_session; conftest.py — use canonical API

## Progress
- Existing code: Base, engine_from_url, session_factory already present; 8/8 tests passing
- Adding engine_factory alias, get_session context manager
- Updating conftest.py to use engine_factory + get_session
