from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text,
)

from app.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=now_utc)


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nationality = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    visa_type = Column(String, nullable=False)
    travel_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=now_utc)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    url = Column(String, nullable=False)
    rank = Column(Integer, default=0)
    is_official = Column(Boolean, default=False)
    status = Column(String, default="ok")  # ok / blocked / error


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    content_hash = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    items_json = Column(Text, nullable=True)
    fetched_at = Column(DateTime, default=now_utc)


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    name = Column(String, nullable=False)
    required = Column(Boolean, default=True)
    details = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending / done
    source_url = Column(String, nullable=False)
    passage = Column(Text, nullable=False)
    last_checked = Column(DateTime, default=now_utc)


class Change(Base):
    __tablename__ = "changes"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    item_name = Column(String, nullable=False)
    change_type = Column(String, nullable=False)  # added / removed / modified
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    passage = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    detected_at = Column(DateTime, default=now_utc)
    is_simulated = Column(Boolean, default=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_id = Column(Integer, ForeignKey("changes.id"), nullable=False)
    seen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now_utc)
    