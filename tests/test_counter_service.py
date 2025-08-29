import pytest
from datetime import datetime
from app.counter_service import CounterService
from app.models import CounterCreate, CounterUpdate
from app.database import reset_db


@pytest.fixture()
def new_db():
    """Reset database for clean test state."""
    reset_db()
    yield
    reset_db()


def test_get_or_create_default_counter(new_db):
    """Test getting or creating the default counter."""
    # Should create new counter on first call
    counter1 = CounterService.get_or_create_default_counter()
    assert counter1 is not None
    assert counter1.name == "default"
    assert counter1.value == 0
    assert counter1.id is not None

    # Should return existing counter on subsequent calls
    counter2 = CounterService.get_or_create_default_counter()
    assert counter2.id == counter1.id
    assert counter2.name == counter1.name
    assert counter2.value == counter1.value


def test_create_counter(new_db):
    """Test creating a new counter."""
    counter_data = CounterCreate(name="test_counter", value=5)
    counter = CounterService.create_counter(counter_data)

    assert counter is not None
    assert counter.name == "test_counter"
    assert counter.value == 5
    assert counter.id is not None
    assert isinstance(counter.created_at, datetime)
    assert isinstance(counter.updated_at, datetime)


def test_get_counter(new_db):
    """Test getting a counter by ID."""
    # Create a counter first
    counter_data = CounterCreate(name="test_counter", value=10)
    created_counter = CounterService.create_counter(counter_data)

    # Get the counter
    if created_counter.id is not None:
        retrieved_counter = CounterService.get_counter(created_counter.id)
        assert retrieved_counter is not None
        assert retrieved_counter.id == created_counter.id
        assert retrieved_counter.name == "test_counter"
        assert retrieved_counter.value == 10

    # Test getting non-existent counter
    non_existent = CounterService.get_counter(99999)
    assert non_existent is None


def test_increment_counter(new_db):
    """Test incrementing a counter."""
    # Create a counter
    counter_data = CounterCreate(name="increment_test", value=5)
    counter = CounterService.create_counter(counter_data)
    original_updated_at = counter.updated_at

    # Increment the counter
    if counter.id is not None:
        updated_counter = CounterService.increment_counter(counter.id)
        assert updated_counter is not None
        assert updated_counter.value == 6
        assert updated_counter.updated_at > original_updated_at

    # Test incrementing non-existent counter
    result = CounterService.increment_counter(99999)
    assert result is None


def test_decrement_counter(new_db):
    """Test decrementing a counter."""
    # Create a counter
    counter_data = CounterCreate(name="decrement_test", value=10)
    counter = CounterService.create_counter(counter_data)
    original_updated_at = counter.updated_at

    # Decrement the counter
    if counter.id is not None:
        updated_counter = CounterService.decrement_counter(counter.id)
        assert updated_counter is not None
        assert updated_counter.value == 9
        assert updated_counter.updated_at > original_updated_at

        # Test decrementing into negative numbers
        for _ in range(20):  # Decrement many times
            CounterService.decrement_counter(counter.id)

        final_counter = CounterService.get_counter(counter.id)
        assert final_counter is not None
        assert final_counter.value < 0  # Should allow negative values

    # Test decrementing non-existent counter
    result = CounterService.decrement_counter(99999)
    assert result is None


def test_update_counter(new_db):
    """Test updating a counter."""
    # Create a counter
    counter_data = CounterCreate(name="update_test", value=15)
    counter = CounterService.create_counter(counter_data)
    original_updated_at = counter.updated_at

    # Update the counter value
    if counter.id is not None:
        update_data = CounterUpdate(value=25)
        updated_counter = CounterService.update_counter(counter.id, update_data)
        assert updated_counter is not None
        assert updated_counter.value == 25
        assert updated_counter.updated_at > original_updated_at

        # Update with None value (should not change)
        update_data_none = CounterUpdate(value=None)
        unchanged_counter = CounterService.update_counter(counter.id, update_data_none)
        assert unchanged_counter is not None
        assert unchanged_counter.value == 25  # Should remain unchanged

    # Test updating non-existent counter
    update_data_test = CounterUpdate(value=25)
    result = CounterService.update_counter(99999, update_data_test)
    assert result is None


def test_reset_counter(new_db):
    """Test resetting a counter to zero."""
    # Create a counter with non-zero value
    counter_data = CounterCreate(name="reset_test", value=42)
    counter = CounterService.create_counter(counter_data)

    # Reset the counter
    if counter.id is not None:
        reset_counter = CounterService.reset_counter(counter.id)
        assert reset_counter is not None
        assert reset_counter.value == 0

    # Test resetting non-existent counter
    result = CounterService.reset_counter(99999)
    assert result is None


def test_multiple_counters(new_db):
    """Test working with multiple independent counters."""
    # Create multiple counters
    counter1 = CounterService.create_counter(CounterCreate(name="counter1", value=1))
    counter2 = CounterService.create_counter(CounterCreate(name="counter2", value=2))
    default_counter = CounterService.get_or_create_default_counter()

    # Increment each counter differently
    if counter1.id is not None:
        CounterService.increment_counter(counter1.id)
        CounterService.increment_counter(counter1.id)  # counter1 should be 3

    if counter2.id is not None:
        CounterService.decrement_counter(counter2.id)  # counter2 should be 1

    if default_counter.id is not None:
        CounterService.increment_counter(default_counter.id)  # default should be 1

    # Verify each counter has correct value
    if counter1.id is not None:
        final_counter1 = CounterService.get_counter(counter1.id)
        assert final_counter1 is not None
        assert final_counter1.value == 3

    if counter2.id is not None:
        final_counter2 = CounterService.get_counter(counter2.id)
        assert final_counter2 is not None
        assert final_counter2.value == 1

    if default_counter.id is not None:
        final_default = CounterService.get_counter(default_counter.id)
        assert final_default is not None
        assert final_default.value == 1


def test_counter_persistence(new_db):
    """Test that counter changes persist across service calls."""
    # Create and modify a counter
    counter = CounterService.create_counter(CounterCreate(name="persist_test", value=0))

    if counter.id is not None:
        # Perform multiple operations
        for i in range(5):
            CounterService.increment_counter(counter.id)

        for i in range(2):
            CounterService.decrement_counter(counter.id)

        # Verify final state
        final_counter = CounterService.get_counter(counter.id)
        assert final_counter is not None
        assert final_counter.value == 3  # 0 + 5 - 2 = 3
