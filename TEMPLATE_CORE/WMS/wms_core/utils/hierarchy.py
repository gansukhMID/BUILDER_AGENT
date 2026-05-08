from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from wms_core.models.location import Location


def build_full_path(location: Location) -> str:
    """Return the full slash-delimited path for a location (same as complete_name)."""
    parts = [location.name]
    node = location.parent
    while node is not None:
        parts.append(node.name)
        node = node.parent
    return "/".join(reversed(parts))


def get_all_children(location_id: int, session: Session) -> list[Location]:
    """Return all descendant Location objects for the given location (excluding itself)."""
    from wms_core.models.location import Location

    sql = text("""
        WITH RECURSIVE descendants AS (
            SELECT id FROM stock_location WHERE parent_id = :loc_id
            UNION ALL
            SELECT l.id FROM stock_location l
            INNER JOIN descendants d ON l.parent_id = d.id
        )
        SELECT id FROM descendants
    """)
    rows = session.execute(sql, {"loc_id": location_id}).fetchall()
    ids = [row[0] for row in rows]
    if not ids:
        return []
    return session.query(Location).filter(Location.id.in_(ids)).all()
