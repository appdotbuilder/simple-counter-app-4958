import pytest
from app.counter_service import CounterService
from app.models import CounterCreate, CounterUpdate
from app.database import reset_db, get_session
from sqlmodel import select
from app.models import Counter


@pytest.fixture()
def new_db():
    """Reset database for clean test state."""
    reset_db()
    yield
    reset_db()


def test_counter_database_persistence(new_db):
    """Test that counter operations properly persist to database."""
    # Create a counter using the service
    counter_data = CounterCreate(name="persistence_test", value=0)
    counter = CounterService.create_counter(counter_data)

    # Verify it exists in database
    with get_session() as session:
        db_counter = session.get(Counter, counter.id)
        assert db_counter is not None
        assert db_counter.value == 0
        assert db_counter.name == "persistence_test"

    # Increment using service
    if counter.id is not None:
        CounterService.increment_counter(counter.id)

        # Verify change persisted to database
        with get_session() as session:
            db_counter = session.get(Counter, counter.id)
            assert db_counter is not None
            assert db_counter.value == 1

        # Decrement using service
        CounterService.decrement_counter(counter.id)

        # Verify change persisted to database
        with get_session() as session:
            db_counter = session.get(Counter, counter.id)
            assert db_counter is not None
            assert db_counter.value == 0


def test_default_counter_singleton_behavior(new_db):
    """Test that default counter behaves as a singleton."""
    # Get default counter multiple times
    counter1 = CounterService.get_or_create_default_counter()
    counter2 = CounterService.get_or_create_default_counter()
    counter3 = CounterService.get_or_create_default_counter()

    # All should be the same instance
    assert counter1.id == counter2.id == counter3.id
    assert counter1.name == counter2.name == counter3.name == "default"

    # Verify only one default counter exists in database
    with get_session() as session:
        statement = select(Counter).where(Counter.name == "default")
        default_counters = session.exec(statement).all()
        assert len(default_counters) == 1
        assert default_counters[0].id == counter1.id


def test_concurrent_counter_operations(new_db):
    """Test that multiple operations on same counter work correctly."""
    # Create a counter
    counter = CounterService.create_counter(CounterCreate(name="concurrent_test", value=0))

    # Capture counter ID safely for lambda functions
    counter_id = counter.id
    assert counter_id is not None

    # Simulate multiple operations that might happen concurrently
    operations = [
        lambda cid=counter_id: CounterService.increment_counter(cid),
        lambda cid=counter_id: CounterService.increment_counter(cid),
        lambda cid=counter_id: CounterService.decrement_counter(cid),
        lambda cid=counter_id: CounterService.increment_counter(cid),
        lambda cid=counter_id: CounterService.increment_counter(cid),
        lambda cid=counter_id: CounterService.decrement_counter(cid),
        lambda cid=counter_id: CounterService.decrement_counter(cid),
    ]

    # Execute all operations
    for operation in operations:
        result = operation()
        assert result is not None  # Each operation should succeed

    # Final value should be: 0 + 2 - 1 + 2 - 2 = 1
    if counter.id is not None:
        final_counter = CounterService.get_counter(counter.id)
        assert final_counter is not None
        assert final_counter.value == 1


def test_counter_timestamp_updates(new_db):
    """Test that updated_at timestamp changes with operations."""
    counter = CounterService.create_counter(CounterCreate(name="timestamp_test", value=0))
    original_updated_at = counter.updated_at

    # Wait a bit then increment to ensure timestamp difference
    import time

    time.sleep(0.01)  # Small delay to ensure timestamp difference

    if counter.id is not None:
        updated_counter = CounterService.increment_counter(counter.id)
        assert updated_counter is not None
        assert updated_counter.updated_at > original_updated_at

        # Another operation should update timestamp again
        second_update_time = updated_counter.updated_at
        time.sleep(0.01)

        final_counter = CounterService.decrement_counter(counter.id)
        assert final_counter is not None
        assert final_counter.updated_at > second_update_time


def test_counter_update_operations(new_db):
    """Test direct update operations through the service."""
    counter = CounterService.create_counter(CounterCreate(name="update_test", value=5))

    # Test updating to specific value
    if counter.id is not None:
        updated = CounterService.update_counter(counter.id, CounterUpdate(value=100))
        assert updated is not None
        assert updated.value == 100

        # Verify in database
        with get_session() as session:
            db_counter = session.get(Counter, counter.id)
            assert db_counter is not None
            assert db_counter.value == 100

        # Test reset operation
        reset_counter = CounterService.reset_counter(counter.id)
        assert reset_counter is not None
        assert reset_counter.value == 0

        # Verify reset persisted
        with get_session() as session:
            db_counter = session.get(Counter, counter.id)
            assert db_counter is not None
            assert db_counter.value == 0


def test_error_handling_with_database(new_db):
    """Test error handling when counter doesn't exist in database."""
    # Try to operate on non-existent counter
    non_existent_id = 99999

    # All operations should return None for non-existent counter
    assert CounterService.get_counter(non_existent_id) is None
    assert CounterService.increment_counter(non_existent_id) is None
    assert CounterService.decrement_counter(non_existent_id) is None
    assert CounterService.update_counter(non_existent_id, CounterUpdate(value=10)) is None
    assert CounterService.reset_counter(non_existent_id) is None

    # Database should remain clean
    with get_session() as session:
        db_counter = session.get(Counter, non_existent_id)
        assert db_counter is None
