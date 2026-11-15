"""Main window: tabs, Manager/Student switch, menu bar, About dialog (owner: Jiya).

``launch_app()`` is the function listed in the README interface contract (7.2).
"""

from __future__ import annotations

import sys
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import messagebox, ttk

# allow `python ui/app.py` as well as `python main.py`
_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ui.charts_panel import ChartsPanel  # noqa: E402
from ui.compare_panel import ComparePanel  # noqa: E402
from ui.input_panel import InputPanel  # noqa: E402
from ui.results_panel import ReportsPanel, ResultsPanel  # noqa: E402
from ui.student_view import StudentView  # noqa: E402
from ui.styles import apply_theme  # noqa: E402

APP_TITLE = "VJTI Canteen Queue & Service Simulator"
TEAM = "Aarya, Chaiti, Janhavi and Jiya"


class CanteenApp(tk.Tk):
    """Top-level window that owns the shared state and connects all panels."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1150x760")
        self.minsize(960, 640)
        apply_theme(self)
        self.report_callback_exception = self._on_tk_error  # friendly errors, no crash

        self.result: dict | None = None
        self._view = tk.StringVar(value="manager")

        self._build_menu()
        self._build_header()
        self._build_body()
        self._build_statusbar()
        self.show_manager()

    # ------------------------------------------------------------------ build
    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_radiobutton(label="Manager view", variable=self._view,
                                  value="manager", command=self.show_manager)
        view_menu.add_radiobutton(label="Student view", variable=self._view,
                                  value="student", command=self.show_student)
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.configure(menu=menubar)

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 12))
        header.pack(fill="x")
        titles = ttk.Frame(header, style="Header.TFrame")
        titles.pack(side="left")
        ttk.Label(titles, text="VJTI Canteen Simulator", style="HeaderTitle.TLabel").pack(anchor="w")
        ttk.Label(titles, text="How long do students wait, and what would change it?",
                  style="HeaderSub.TLabel").pack(anchor="w")
        switch = ttk.Frame(header, style="Header.TFrame")
        switch.pack(side="right")
        ttk.Button(switch, text="Manager view", style="Switch.TButton",
                   command=self.show_manager).pack(side="left", padx=4)
        ttk.Button(switch, text="Student view", style="Switch.TButton",
                   command=self.show_student).pack(side="left")

    def _build_body(self) -> None:
        self._body = ttk.Frame(self)
        self._body.pack(fill="both", expand=True)

        # Manager view: tabs
        self._manager = ttk.Notebook(self._body)
        self.results_panel = ResultsPanel(self._manager)
        self.charts_panel = ChartsPanel(self._manager)
        self.compare_panel = ComparePanel(self._manager)
        self.reports_panel = ReportsPanel(self._manager)
        self.input_panel = InputPanel(self._manager, on_complete=self.on_result,
                                      on_status=self.set_status)
        self._manager.add(self.input_panel, text="  Run Simulation  ")
        self._manager.add(self.results_panel, text="  Results  ")
        self._manager.add(self.charts_panel, text="  Charts  ")
        self._manager.add(self.compare_panel, text="  Compare Scenarios  ")
        self._manager.add(self.reports_panel, text="  Reports  ")

        # Student view
        self._student = StudentView(self._body, on_need_data=self.show_manager)

    def _build_statusbar(self) -> None:
        self._status = tk.StringVar(value="Ready.")
        bar = ttk.Frame(self, padding=(14, 4))
        bar.pack(fill="x", side="bottom")
        ttk.Label(bar, textvariable=self._status, style="Muted.TLabel").pack(side="left")

    # ------------------------------------------------------------------ views
    def show_manager(self) -> None:
        self._view.set("manager")
        self._student.pack_forget()
        self._manager.pack(fill="both", expand=True, padx=12, pady=12)

    def show_student(self) -> None:
        self._view.set("student")
        self._manager.pack_forget()
        self._student.pack(fill="both", expand=True, padx=12, pady=12)
        if self.result is None:
            self._student.show_no_data_hint()

    # ---------------------------------------------------------------- results
    def on_result(self, result: dict) -> None:
        """Called by the Run tab (main thread) when a run finishes."""
        self.result = result
        self.results_panel.update_results(result)
        self.charts_panel.update_results(result)
        self.compare_panel.update_results(result)
        self.reports_panel.set_result(result)
        self._student.update_results(result)
        self.set_status("Results updated.")
        self._manager.select(self.results_panel)

    def set_status(self, text: str) -> None:
        self._status.set(text)

    # ----------------------------------------------------------------- dialogs
    def show_about(self) -> None:
        messagebox.showinfo(
            "About",
            f"{APP_TITLE}\n\nPython Mini Project, Second Year B.Tech IT, VJTI\n"
            f"Team: {TEAM}\n\nA minute-by-minute simulation of the canteen using "
            "Negative Binomial arrivals, with analysis and what-if scenarios.")

    def _on_tk_error(self, exc_type, exc_value, exc_tb) -> None:
        traceback.print_exception(exc_type, exc_value, exc_tb)
        messagebox.showerror(
            "Something went wrong",
            f"The app hit an unexpected problem:\n\n{exc_value}\n\n"
            "You can keep using it; if this repeats, tell the team what you clicked.")


def launch_app() -> None:
    """Instantiate and launch the Tkinter desktop GUI."""
    app = CanteenApp()
    app.mainloop()


if __name__ == "__main__":
    launch_app()
