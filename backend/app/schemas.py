from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, computed_field, field_validator

# ---- MVP corridors (design rule 6): India -> Germany / UK / Canada, student visa
SUPPORTED_NATIONALITY = "India"
SUPPORTED_VISA_TYPE = "student"
DESTINATION_ALIASES = {
    "germany": "Germany",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "canada": "Canada",
}


# ---------------------------------------------------------------- requests
class TripCreate(BaseModel):
    nationality: str
    destination: str
    visa_type: str
    travel_date: date

    @field_validator("nationality")
    @classmethod
    def check_nationality(cls, v: str) -> str:
        if v.strip().lower() != SUPPORTED_NATIONALITY.lower():
            raise ValueError(f"MVP supports nationality '{SUPPORTED_NATIONALITY}' only")
        return SUPPORTED_NATIONALITY

    @field_validator("destination")
    @classmethod
    def check_destination(cls, v: str) -> str:
        canonical = DESTINATION_ALIASES.get(v.strip().lower())
        if canonical is None:
            raise ValueError("MVP supports destinations: Germany, United Kingdom, Canada")
        return canonical

    @field_validator("visa_type")
    @classmethod
    def check_visa_type(cls, v: str) -> str:
        if v.strip().lower() != SUPPORTED_VISA_TYPE:
            raise ValueError(f"MVP supports visa type '{SUPPORTED_VISA_TYPE}' only")
        return SUPPORTED_VISA_TYPE

    @field_validator("travel_date")
    @classmethod
    def check_travel_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("travel_date cannot be in the past")
        return v


class ChecklistItemUpdate(BaseModel):
    status: Literal["pending", "done"]


# --------------------------------------------------------------- responses
class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    rank: int
    is_official: bool
    status: Literal["ok", "blocked", "error"]

    @computed_field
    @property
    def could_not_verify(self) -> bool:
        # Design rule 4: anything not "ok" must show "could not verify" in the UI
        return self.status != "ok"


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nationality: str
    destination: str
    visa_type: str
    travel_date: date
    created_at: datetime
    sources: list[SourceOut] = []


class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    name: str
    required: bool
    details: str | None = None
    status: Literal["pending", "done"]
    source_url: str
    passage: str
    last_checked: datetime


class ChangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    item_name: str
    change_type: Literal["added", "removed", "modified"]
    old_value: str | None = None
    new_value: str | None = None
    passage: str | None = None
    source_url: str | None = None
    detected_at: datetime
    is_simulated: bool


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seen: bool
    created_at: datetime
    change: ChangeOut