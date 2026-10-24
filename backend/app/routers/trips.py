from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio

from app import models, schemas
from app.database import get_db
from app.services import tinyfish
from app.services.extractor import extract_requirements

router = APIRouter(prefix="/trips", tags=["trips"])

# TEMP (remove in Phase 2): fixed user until real login exists
TEMP_USER_ID = 1


def _ensure_temp_user(db: Session) -> None:
    """TEMP (remove in Phase 2): make sure the fixed user row exists."""
    if db.get(models.User, TEMP_USER_ID) is None:
        db.add(models.User(
            id=TEMP_USER_ID,
            email="temp@example.com",
            password_hash="TEMP-NOT-A-REAL-HASH",
        ))
        db.commit()


def _get_trip_or_404(trip_id: int, db: Session) -> models.Trip:
    trip = db.get(models.Trip, trip_id)
    # TEMP (Phase 2): compare with the logged-in user instead of TEMP_USER_ID
    if trip is None or trip.user_id != TEMP_USER_ID:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def _save_checklist_items(
    trip_id: int,
    items: list[dict],
    source_url: str,
    snapshot_fetched_at,
    db: Session,
) -> None:
    """Save extracted items to checklist_items table. Skip duplicates by name."""
    existing_names = {
        row.name
        for row in db.query(models.ChecklistItem.name)
        .filter(models.ChecklistItem.trip_id == trip_id)
        .all()
    }
    for item in items:
        name = item.get("name", "").strip()
        if not name or name in existing_names:
            continue
        db.add(models.ChecklistItem(
            trip_id=trip_id,
            name=name,
            required=item.get("required", True),
            details=item.get("details", ""),
            status="pending",
            source_url=source_url,
            passage=item.get("passage", ""),
            last_checked=snapshot_fetched_at,
        ))
        existing_names.add(name)


@router.post("", response_model=schemas.TripOut, status_code=201)
def create_trip(payload: schemas.TripCreate, db: Session = Depends(get_db)):
    """Create a trip, find official pages, fetch them, extract requirements."""
    _ensure_temp_user(db)

    trip = models.Trip(user_id=TEMP_USER_ID, **payload.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # 1. Search (official domains only)
    try:
        found = tinyfish.search_official(trip.destination)
    except tinyfish.TinyFishError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not search for official sources: {exc}",
        )

    # 2. Fetch all found pages in one call
    pages = tinyfish.fetch([item["url"] for item in found])

    # 3. Save sources + snapshots, then extract checklist items
    for item, page in zip(found, pages):
        source = models.Source(
            trip_id=trip.id,
            url=item["url"],
            rank=item["rank"],
            is_official=True,
            status=page["status"],
        )
        db.add(source)
        db.flush()

        if page["status"] == "ok":
            snapshot = models.Snapshot(
                source_id=source.id,
                content_hash=tinyfish.content_hash(page["text"]),
                raw_text=page["text"],
            )
            db.add(snapshot)
            db.flush()

            # 4. Extract requirements from this page
            extracted = asyncio.run(extract_requirements(page["text"]))

            # 5. Save valid items to checklist
            _save_checklist_items(
                trip_id=trip.id,
                items=extracted,
                source_url=item["url"],
                snapshot_fetched_at=snapshot.fetched_at,
                db=db,
            )

    db.commit()
    db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return _get_trip_or_404(trip_id, db)


@router.get("/{trip_id}/checklist", response_model=list[schemas.ChecklistItemOut])
def get_checklist(trip_id: int, db: Session = Depends(get_db)):
    """Returns saved checklist items for a trip."""
    _get_trip_or_404(trip_id, db)
    return (
        db.query(models.ChecklistItem)
        .filter(models.ChecklistItem.trip_id == trip_id)
        .all()
    )