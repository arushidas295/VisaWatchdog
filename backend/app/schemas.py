from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TripCreate(BaseModel):
    nationality: str
    destination: str
    visa_type: str
    travel_date: Optional[date] = None


class TripOut(BaseModel):
    id: int
    nationality: str
    destination: str
    visa_type: str
    travel_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChecklistItemOut(BaseModel):
    id: int
    name: str
    required: bool
    details: Optional[str] = None
    status: str
    source_url: str
    passage: str
    last_checked: datetime

    class Config:
        from_attributes = True