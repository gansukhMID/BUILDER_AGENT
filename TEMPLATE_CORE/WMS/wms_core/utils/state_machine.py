from typing import Any


class InvalidTransition(Exception):
    pass


PICKING_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["confirmed", "cancelled"],
    "confirmed": ["in_progress", "cancelled"],
    "in_progress": ["done", "cancelled"],
    "done": [],
    "cancelled": [],
}


class StateMachine:
    def __init__(self, transitions: dict[str, list[str]]) -> None:
        self._transitions = transitions

    def can(self, current_state: str, target_state: str) -> bool:
        return target_state in self._transitions.get(current_state, [])

    def apply(self, obj: Any, state_attr: str, target_state: str) -> None:
        current = getattr(obj, state_attr)
        current_val = current.value if hasattr(current, "value") else current
        if not self.can(current_val, target_state):
            allowed = self._transitions.get(current_val, [])
            raise InvalidTransition(
                f"Cannot transition from '{current_val}' to '{target_state}'. "
                f"Allowed: {allowed}"
            )
        setattr(obj, state_attr, target_state)


def transition(current: str, target: str) -> str:
    """Validate and return the new state. Raises ValueError on invalid transition."""
    allowed = PICKING_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise ValueError(
            f"Cannot transition picking from '{current}' to '{target}'. "
            f"Allowed: {allowed}"
        )
    return target
