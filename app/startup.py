from app.database import create_tables
from nicegui import ui
import app.counter_ui


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Register counter UI module
    app.counter_ui.create()

    @ui.page("/")
    def index():
        """Home page with navigation to counter app."""
        with ui.column().classes("items-center mt-16 gap-8"):
            ui.label("Welcome to the Counter App").classes("text-4xl font-bold text-gray-800")
            ui.label("A simple counter application with increment and decrement functionality").classes(
                "text-lg text-gray-600 text-center max-w-md"
            )

            # Navigation card
            with ui.card().classes("p-6 shadow-lg rounded-xl bg-white"):
                ui.label("Get Started").classes("text-xl font-bold text-gray-800 mb-4")
                ui.link("Open Counter App →", "/counter").classes(
                    "bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold no-underline inline-block"
                )
