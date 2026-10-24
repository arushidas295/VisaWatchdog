from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/trips", tags=["trips"])

# TEMPORARY: Phase 2 mein ise asli logged-in user se badlenge
TEMP_USER_ID = 1


@router.post("", response_model=schemas.TripOut)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    db_trip = models.Trip(user_id=TEMP_USER_ID, **trip.model_dump())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@router.get("/{trip_id}", response_model=schemas.TripOut)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.get("/{trip_id}/checklist", response_model=list[schemas.ChecklistItemOut])
def get_checklist(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return (
        db.query(models.ChecklistItem)
        .filter(models.ChecklistItem.trip_id == trip_id)
        .all()
    )