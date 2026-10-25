# backend/app/routers/checklist.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/checklist", tags=["checklist"])

TEMP_USER_ID = 1


@router.patch("/{item_id}", response_model=schemas.ChecklistItemOut)
def update_item(item_id: int, payload: schemas.ChecklistItemUpdate, db: Session = Depends(get_db)):
    """Mark a checklist item as done or pending."""
    item = db.get(models.ChecklistItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    trip = db.get(models.Trip, item.trip_id)
    if not trip or trip.user_id != TEMP_USER_ID:
        raise HTTPException(status_code=404, detail="Item not found")

    if payload.status is not None:
        item.status = payload.status
    db.commit()
    db.refresh(item)
    return item