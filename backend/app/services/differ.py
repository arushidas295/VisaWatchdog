# backend/app/services/differ.py
from datetime import datetime, timezone
from app import models
from sqlalchemy.orm import Session


def _normalize(name: str) -> str:
    """Normalize item name for comparison (lowercase, stripped)."""
    return name.strip().lower()


def compute_diff(trip_id: int, new_items: list[dict], db: Session) -> list[models.Change]:
    """
    Compare new_items against the current checklist_items in the DB.
    Returns a list of Change objects (not yet committed).
    """
    # Load existing checklist items for this trip
    existing = db.query(models.ChecklistItem).filter(
        models.ChecklistItem.trip_id == trip_id
    ).all()

    existing_map = {_normalize(item.name): item for item in existing}
    new_map = {_normalize(item.get("name", "")): item for item in new_items}

    changes = []
    now = datetime.now(timezone.utc)

    # Check for added and modified items
    for norm_name, new_item in new_map.items():
        if not norm_name:
            continue

        if norm_name not in existing_map:
            # Brand new item
            changes.append(models.Change(
                trip_id=trip_id,
                item_name=new_item.get("name", norm_name),
                change_type="added",
                old_value=None,
                new_value=new_item.get("details") or str(new_item.get("required")),
                passage=new_item.get("passage", ""),
                source_url=new_item.get("source_url", ""),
                detected_at=now,
                is_simulated=False,
            ))
        else:
            old_item = existing_map[norm_name]
            # Check if required or details changed
            old_val = f"required={old_item.required} | {old_item.details or ''}"
            new_val = f"required={new_item.get('required', True)} | {new_item.get('details', '') or ''}"
            if old_val != new_val:
                changes.append(models.Change(
                    trip_id=trip_id,
                    item_name=new_item.get("name", norm_name),
                    change_type="modified",
                    old_value=old_val,
                    new_value=new_val,
                    passage=new_item.get("passage", ""),
                    source_url=new_item.get("source_url", ""),
                    detected_at=now,
                    is_simulated=False,
                ))

    # Check for removed items
    for norm_name, old_item in existing_map.items():
        if norm_name not in new_map:
            changes.append(models.Change(
                trip_id=trip_id,
                item_name=old_item.name,
                change_type="removed",
                old_value=old_item.details or str(old_item.required),
                new_value=None,
                passage=old_item.passage or "",
                source_url=old_item.source_url or "",
                detected_at=now,
                is_simulated=False,
            ))

    return changes


def update_checklist(trip_id: int, new_items: list[dict], db: Session) -> None:
    """Update checklist_items table with new extracted items."""
    existing = db.query(models.ChecklistItem).filter(
        models.ChecklistItem.trip_id == trip_id
    ).all()
    existing_map = {_normalize(item.name): item for item in existing}

    for new_item in new_items:
        norm_name = _normalize(new_item.get("name", ""))
        if not norm_name:
            continue
        if norm_name in existing_map:
            # Update existing
            old = existing_map[norm_name]
            old.required = new_item.get("required", old.required)
            old.details = new_item.get("details", old.details)
            old.passage = new_item.get("passage", old.passage)
            old.last_checked = datetime.now(timezone.utc)
        else:
            # Add new
            db.add(models.ChecklistItem(
                trip_id=trip_id,
                name=new_item.get("name", ""),
                required=new_item.get("required", True),
                details=new_item.get("details", ""),
                status="pending",
                source_url=new_item.get("source_url", ""),
                passage=new_item.get("passage", ""),
                last_checked=datetime.now(timezone.utc),
            ))