import pytest
from nicegui.testing import User
from app.database import reset_db
from app.counter_service import CounterService
from app.models import CounterCreate


@pytest.fixture()
def new_db():
    """Reset database for clean test state."""
    reset_db()
    yield
    reset_db()


async def test_counter_page_loads(user: User, new_db) -> None:
    """Test that the counter page loads correctly."""
    await user.open("/counter")

    # Check page elements are present
    await user.should_see("Counter Application")
    await user.should_see("Count:")
    await user.should_see(marker="counter-value")
    await user.should_see(marker="increment-button")
    await user.should_see(marker="decrement-button")
    await user.should_see(marker="reset-button")


async def test_counter_increment(user: User, new_db) -> None:
    """Test incrementing the counter."""
    await user.open("/counter")

    # Initially should show 0
    await user.should_see("0")

    # Click increment button
    user.find(marker="increment-button").click()
    await user.should_see("Counter incremented!")

    # Counter should now show 1
    await user.should_see("1")

    # Click increment again
    user.find(marker="increment-button").click()
    await user.should_see("Counter incremented!")

    # Counter should now show 2
    await user.should_see("2")


async def test_counter_decrement(user: User, new_db) -> None:
    """Test decrementing the counter."""
    # Create a counter with initial value for testing
    CounterService.create_counter(CounterCreate(name="default", value=5))

    await user.open("/counter")

    # Should show initial value of 5
    await user.should_see("5")

    # Click decrement button
    user.find(marker="decrement-button").click()
    await user.should_see("Counter decremented!")

    # Counter should now show 4
    await user.should_see("4")

    # Click decrement again
    user.find(marker="decrement-button").click()
    await user.should_see("Counter decremented!")

    # Counter should now show 3
    await user.should_see("3")


async def test_counter_reset(user: User, new_db) -> None:
    """Test resetting the counter."""
    await user.open("/counter")

    # Wait for page to fully load
    await user.should_see("Counter Application")
    await user.should_see("0")  # Should start at 0

    # Increment counter a few times first
    for _ in range(3):
        increment_button = user.find(marker="increment-button")
        increment_button.click()
        await user.should_see("Counter incremented!")

    # Verify it shows 3
    await user.should_see("3")

    # Click reset button
    reset_button = user.find(marker="reset-button")
    reset_button.click()
    await user.should_see("Counter reset to 0!")

    # Counter should now show 0
    await user.should_see("0")


async def test_counter_negative_values(user: User, new_db) -> None:
    """Test that counter can go negative."""
    await user.open("/counter")

    # Wait for page to load
    await user.should_see("Counter Application")
    await user.should_see("0")

    # Counter starts at 0, decrement it
    decrement_button = user.find(marker="decrement-button")
    decrement_button.click()
    await user.should_see("Counter decremented!")

    # Should show -1
    await user.should_see("-1")

    # Decrement again
    decrement_button = user.find(marker="decrement-button")
    decrement_button.click()
    await user.should_see("Counter decremented!")

    # Should show -2
    await user.should_see("-2")


async def test_counter_multiple_operations(user: User, new_db) -> None:
    """Test multiple counter operations in sequence."""
    await user.open("/counter")

    # Wait for page to load
    await user.should_see("Counter Application")
    await user.should_see("0")

    # Start at 0, perform various operations
    operations = [
        ("increment-button", "1"),
        ("increment-button", "2"),
        ("increment-button", "3"),
        ("decrement-button", "2"),
        ("increment-button", "3"),
        ("decrement-button", "2"),
        ("decrement-button", "1"),
        ("decrement-button", "0"),
        ("decrement-button", "-1"),
    ]

    for button_marker, expected_value in operations:
        button = user.find(marker=button_marker)
        button.click()
        # Wait for the operation to complete (notification appears)
        if "increment" in button_marker:
            await user.should_see("Counter incremented!")
        else:
            await user.should_see("Counter decremented!")

        # Verify the counter shows expected value
        await user.should_see(expected_value)


async def test_home_page_navigation(user: User, new_db) -> None:
    """Test navigation from home page to counter."""
    await user.open("/")

    # Check home page elements
    await user.should_see("Welcome to the Counter App")
    await user.should_see("Get Started")

    # Click the link to counter app
    user.find("Open Counter App →").click()

    # Should navigate to counter page
    await user.should_see("Counter Application")
    await user.should_see(marker="counter-value")


async def test_specific_counter_page_not_found(user: User, new_db) -> None:
    """Test accessing a non-existent counter by ID."""
    await user.open("/counter/99999")

    # Should show not found message
    await user.should_see("Counter Not Found")
    await user.should_see("Counter with ID 99999 does not exist.")
    await user.should_see("← Go to Default Counter")


async def test_specific_counter_page_exists(user: User, new_db) -> None:
    """Test accessing an existing counter by ID."""
    # Create a specific counter
    counter = CounterService.create_counter(CounterCreate(name="test_counter", value=10))

    await user.open(f"/counter/{counter.id}")

    # Should show the counter page with the correct value
    await user.should_see("Counter Application")
    await user.should_see("10")
