# backend/app/routers/alerts.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/alerts", tags=["alerts"])

TEMP_USER_ID = 1


@router.get("", response_model=list[schemas.AlertOut])
def get_alerts(db: Session = Depends(get_db)):
    """Return all alerts for the current user, newest first."""
    return (
        db.query(models.Alert)
        .filter(models.Alert.user_id == TEMP_USER_ID)
        .order_by(models.Alert.created_at.desc())
        .all()
    )


@router.patch("/{alert_id}/seen")
def mark_seen(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as seen."""
    alert = db.get(models.Alert, alert_id)
    if alert and alert.user_id == TEMP_USER_ID:
        alert.seen = True
        db.commit()
    return {"ok": True}