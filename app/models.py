from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Counter(SQLModel, table=True):
    """Model to store counter state with increment/decrement capability."""

    __tablename__ = "counters"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, default="default")
    value: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CounterCreate(SQLModel, table=False):
    """Schema for creating a new counter."""

    name: str = Field(max_length=100, default="default")
    value: int = Field(default=0)


class CounterUpdate(SQLModel, table=False):
    """Schema for updating counter value."""

    value: Optional[int] = Field(default=None)
