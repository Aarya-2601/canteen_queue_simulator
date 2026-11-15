"""Desktop app package (owner: Jiya).

``launch_app()`` is the single entry point that ``main.py`` calls.  The import of
the Tkinter window is done lazily inside the function so that the pure-Python
helpers in ``ui.helpers`` can be imported (and unit-tested) on machines or CI
runners that have no display / no Tkinter.
"""


def launch_app() -> None:
    """Create the Tkinter main window and start the event loop."""
    from ui.app import launch_app as _launch

    _launch()


__all__ = ["launch_app"]
