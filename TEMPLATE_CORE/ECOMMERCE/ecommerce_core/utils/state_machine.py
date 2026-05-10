from typing import Any


class InvalidTransition(Exception):
    pass


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
