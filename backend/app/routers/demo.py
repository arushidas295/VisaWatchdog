# backend/app/routers/demo.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/demo", tags=["demo"])

TEMP_USER_ID = 1


@router.post("/simulate-change", response_model=schemas.ChangeOut)
def simulate_change(trip_id: int, db: Session = Depends(get_db)):
    """
    [SIMULATED] Inject a fake visa requirement change for demo purposes.
    Clearly labelled as simulated - never real data.
    """
    trip = db.get(models.Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Create a clearly labelled simulated change
    change = models.Change(
        trip_id=trip_id,
        item_name="Proof of onward travel [SIMULATED]",
        change_type="added",
        old_value=None,
        new_value="Required: confirmed return or onward ticket [SIMULATED CHANGE]",
        passage="Applicants must show proof of onward travel. [SIMULATED - not from official source]",
        source_url="https://www.gov.uk/student-visa [SIMULATED]",
        detected_at=datetime.now(timezone.utc),
        is_simulated=True,
    )
    db.add(change)
    db.flush()

    # Create alert for this simulated change
    alert = models.Alert(
        user_id=TEMP_USER_ID,
        change_id=change.id,
        seen=False,
    )
    db.add(alert)
    db.commit()
    db.refresh(change)

    return change