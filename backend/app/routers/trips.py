from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio
import time

from app import models, schemas
from app.database import get_db
from app.services import tinyfish
from app.services.extractor import extract_requirements

router = APIRouter(prefix="/trips", tags=["trips"])

TEMP_USER_ID = 1


def _ensure_temp_user(db: Session) -> None:
    if db.get(models.User, TEMP_USER_ID) is None:
        db.add(models.User(
            id=TEMP_USER_ID,
            email="temp@example.com",
            password_hash="TEMP-NOT-A-REAL-HASH",
        ))
        db.commit()


def _get_trip_or_404(trip_id: int, db: Session) -> models.Trip:
    trip = db.get(models.Trip, trip_id)
    if trip is None or trip.user_id != TEMP_USER_ID:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def _save_checklist_items(trip_id, items, source_url, snapshot_fetched_at, db):
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
    _ensure_temp_user(db)
    trip = models.Trip(user_id=TEMP_USER_ID, **payload.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)

    try:
        found = tinyfish.search_official(trip.destination)
    except tinyfish.TinyFishError as exc:
        raise HTTPException(status_code=502, detail=f"Search failed: {exc}")

    pages = tinyfish.fetch([item["url"] for item in found])

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
            time.sleep(5)
            extracted = asyncio.run(extract_requirements(page["text"]))
            _save_checklist_items(
                trip.id, extracted, item["url"], snapshot.fetched_at, db
            )

    db.commit()
    db.refresh(trip)
    return trip


@router.get("/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return _get_trip_or_404(trip_id, db)


@router.get("/{trip_id}/checklist", response_model=list[schemas.ChecklistItemOut])
def get_checklist(trip_id: int, db: Session = Depends(get_db)):
    _get_trip_or_404(trip_id, db)
    return (
        db.query(models.ChecklistItem)
        .filter(models.ChecklistItem.trip_id == trip_id)
        .all()
    )