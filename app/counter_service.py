from datetime import datetime
from typing import Optional
from sqlmodel import select
from app.database import get_session
from app.models import Counter, CounterCreate, CounterUpdate


class CounterService:
    """Service layer for counter operations."""

    @staticmethod
    def get_or_create_default_counter() -> Counter:
        """Get the default counter or create it if it doesn't exist."""
        with get_session() as session:
            statement = select(Counter).where(Counter.name == "default")
            counter = session.exec(statement).first()

            if counter is None:
                counter = Counter(name="default", value=0)
                session.add(counter)
                session.commit()
                session.refresh(counter)

            return counter

    @staticmethod
    def get_counter(counter_id: int) -> Optional[Counter]:
        """Get a counter by ID."""
        with get_session() as session:
            return session.get(Counter, counter_id)

    @staticmethod
    def create_counter(counter_data: CounterCreate) -> Counter:
        """Create a new counter."""
        with get_session() as session:
            counter = Counter(name=counter_data.name, value=counter_data.value)
            session.add(counter)
            session.commit()
            session.refresh(counter)
            return counter

    @staticmethod
    def increment_counter(counter_id: int) -> Optional[Counter]:
        """Increment counter value by 1."""
        with get_session() as session:
            counter = session.get(Counter, counter_id)
            if counter is None:
                return None

            counter.value += 1
            counter.updated_at = datetime.utcnow()
            session.add(counter)
            session.commit()
            session.refresh(counter)
            return counter

    @staticmethod
    def decrement_counter(counter_id: int) -> Optional[Counter]:
        """Decrement counter value by 1."""
        with get_session() as session:
            counter = session.get(Counter, counter_id)
            if counter is None:
                return None

            counter.value -= 1
            counter.updated_at = datetime.utcnow()
            session.add(counter)
            session.commit()
            session.refresh(counter)
            return counter

    @staticmethod
    def update_counter(counter_id: int, counter_data: CounterUpdate) -> Optional[Counter]:
        """Update counter with new data."""
        with get_session() as session:
            counter = session.get(Counter, counter_id)
            if counter is None:
                return None

            if counter_data.value is not None:
                counter.value = counter_data.value
                counter.updated_at = datetime.utcnow()
                session.add(counter)
                session.commit()
                session.refresh(counter)

            return counter

    @staticmethod
    def reset_counter(counter_id: int) -> Optional[Counter]:
        """Reset counter value to 0."""
        return CounterService.update_counter(counter_id, CounterUpdate(value=0))
