from nicegui import ui, app
from app.counter_service import CounterService


def create():
    """Create counter UI module."""

    @ui.page("/counter")
    async def counter_page():
        """Counter application page."""
        # Wait for client connection before accessing tab storage
        await ui.context.client.connected()

        # Get or create the default counter
        counter = CounterService.get_or_create_default_counter()

        # Store counter ID in tab storage for this session
        if counter.id is not None:
            app.storage.tab["counter_id"] = counter.id

        # Create refreshable display component
        @ui.refreshable
        def counter_display():
            counter_id = app.storage.tab.get("counter_id")
            if counter_id is None:
                ui.label("No counter ID found").classes("text-red-500")
                return

            current_counter = CounterService.get_counter(counter_id)
            if current_counter is None:
                ui.label("Counter not found").classes("text-red-500")
                return

            # Main counter display
            with ui.card().classes("w-96 p-8 text-center shadow-lg rounded-xl bg-white"):
                ui.label("Counter Application").classes("text-2xl font-bold text-gray-800 mb-6")

                # Counter value display
                with ui.row().classes("justify-center items-center mb-8"):
                    ui.label("Count:").classes("text-lg text-gray-600 mr-4")
                    ui.label(str(current_counter.value)).classes(
                        "text-5xl font-bold text-blue-600 bg-blue-50 px-6 py-3 rounded-lg"
                    ).mark("counter-value")

                # Control buttons
                with ui.row().classes("gap-4 justify-center mb-4"):
                    ui.button("-", on_click=handle_decrement).classes(
                        "bg-red-500 hover:bg-red-600 text-white text-2xl font-bold px-6 py-3 rounded-lg shadow-md"
                    ).props("size=lg").mark("decrement-button")

                    ui.button("+", on_click=handle_increment).classes(
                        "bg-green-500 hover:bg-green-600 text-white text-2xl font-bold px-6 py-3 rounded-lg shadow-md"
                    ).props("size=lg").mark("increment-button")

                # Reset button
                ui.button("Reset", on_click=handle_reset).classes(
                    "bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
                ).props("outline").mark("reset-button")

                # Display last updated time
                if current_counter.updated_at:
                    ui.label(f"Last updated: {current_counter.updated_at.strftime('%Y-%m-%d %H:%M:%S')}").classes(
                        "text-sm text-gray-500 mt-4"
                    )

        def handle_increment():
            """Handle increment button click."""
            counter_id = app.storage.tab.get("counter_id")
            if counter_id is not None:
                result = CounterService.increment_counter(counter_id)
                if result:
                    counter_display.refresh()  # type: ignore
                    ui.notify("Counter incremented!", type="positive")
                else:
                    ui.notify("Failed to increment counter", type="negative")

        def handle_decrement():
            """Handle decrement button click."""
            counter_id = app.storage.tab.get("counter_id")
            if counter_id is not None:
                result = CounterService.decrement_counter(counter_id)
                if result:
                    counter_display.refresh()  # type: ignore
                    ui.notify("Counter decremented!", type="positive")
                else:
                    ui.notify("Failed to decrement counter", type="negative")

        def handle_reset():
            """Handle reset button click."""
            counter_id = app.storage.tab.get("counter_id")
            if counter_id is not None:
                result = CounterService.reset_counter(counter_id)
                if result:
                    counter_display.refresh()  # type: ignore
                    ui.notify("Counter reset to 0!", type="info")
                else:
                    ui.notify("Failed to reset counter", type="negative")

        # Display the counter
        counter_display()

        # Navigation link back to home
        with ui.row().classes("mt-8 justify-center"):
            ui.link("← Back to Home", "/").classes("text-blue-500 hover:text-blue-700")

    @ui.page("/counter/{counter_id:int}")
    async def specific_counter_page(counter_id: int):
        """Page for a specific counter by ID."""
        counter = CounterService.get_counter(counter_id)

        if counter is None:
            with ui.column().classes("items-center mt-8"):
                ui.label("Counter Not Found").classes("text-2xl font-bold text-red-600 mb-4")
                ui.label(f"Counter with ID {counter_id} does not exist.").classes("text-gray-600 mb-4")
                ui.link("← Go to Default Counter", "/counter").classes("text-blue-500 hover:text-blue-700")
            return

        # Wait for client connection before accessing tab storage
        await ui.context.client.connected()

        # Store this counter ID in tab storage
        if counter.id is not None:
            app.storage.tab["counter_id"] = counter.id

        # Show counter name if not default
        if counter.name != "default":
            ui.label(f"Counter: {counter.name}").classes("text-xl font-semibold text-gray-700 mb-4 text-center")

        # Create the counter display inline
        @ui.refreshable
        def counter_display():
            current_counter_id = app.storage.tab.get("counter_id")
            if current_counter_id is None:
                ui.label("No counter ID found").classes("text-red-500")
                return

            current_counter = CounterService.get_counter(current_counter_id)
            if current_counter is None:
                ui.label("Counter not found").classes("text-red-500")
                return

            # Main counter display
            with ui.card().classes("w-96 p-8 text-center shadow-lg rounded-xl bg-white"):
                ui.label("Counter Application").classes("text-2xl font-bold text-gray-800 mb-6")

                # Counter value display
                with ui.row().classes("justify-center items-center mb-8"):
                    ui.label("Count:").classes("text-lg text-gray-600 mr-4")
                    ui.label(str(current_counter.value)).classes(
                        "text-5xl font-bold text-blue-600 bg-blue-50 px-6 py-3 rounded-lg"
                    ).mark("counter-value")

                # Control buttons
                with ui.row().classes("gap-4 justify-center mb-4"):
                    ui.button("-", on_click=handle_decrement).classes(
                        "bg-red-500 hover:bg-red-600 text-white text-2xl font-bold px-6 py-3 rounded-lg shadow-md"
                    ).props("size=lg").mark("decrement-button")

                    ui.button("+", on_click=handle_increment).classes(
                        "bg-green-500 hover:bg-green-600 text-white text-2xl font-bold px-6 py-3 rounded-lg shadow-md"
                    ).props("size=lg").mark("increment-button")

                # Reset button
                ui.button("Reset", on_click=handle_reset).classes(
                    "bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg"
                ).props("outline").mark("reset-button")

                # Display last updated time
                if current_counter.updated_at:
                    ui.label(f"Last updated: {current_counter.updated_at.strftime('%Y-%m-%d %H:%M:%S')}").classes(
                        "text-sm text-gray-500 mt-4"
                    )

        def handle_increment():
            """Handle increment button click."""
            current_counter_id = app.storage.tab.get("counter_id")
            if current_counter_id is not None:
                result = CounterService.increment_counter(current_counter_id)
                if result:
                    counter_display.refresh()  # type: ignore
                    ui.notify("Counter incremented!", type="positive")
                else:
                    ui.notify("Failed to increment counter", type="negative")

        def handle_decrement():
            """Handle decrement button click."""
            current_counter_id = app.storage.tab.get("counter_id")
            if current_counter_id is not None:
                result = CounterService.decrement_counter(current_counter_id)
                if result:
                    counter_display.refresh()  # type: ignore
                    ui.notify("Counter decremented!", type="positive")
                else:
                    ui.notify("Failed to decrement counter", type="negative")

        def handle_reset():
            """Handle reset button click."""
            current_counter_id = app.storage.tab.get("counter_id")
            if current_counter_id is not None:
                result = CounterService.reset_counter(current_counter_id)
                if result:
                    counter_display.refresh()  # type: ignore
                    ui.notify("Counter reset to 0!", type="info")
                else:
                    ui.notify("Failed to reset counter", type="negative")

        # Display the counter
        counter_display()

        # Navigation link back to home
        with ui.row().classes("mt-8 justify-center"):
            ui.link("← Back to Home", "/").classes("text-blue-500 hover:text-blue-700")
