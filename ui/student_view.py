"""Student view: "best time to visit" chart + quickest counter selector (owner: Jiya)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.charts_panel import FigureFrame, build_figure
from ui.helpers import (BackendMissing, best_time, get_open_hour, parse_clock,
                        quickest_counter, time_choices)
from ui.results_panel import fill_tree


class StudentView(ttk.Frame):
    """Simple, friendly view for students - no settings, just answers."""

    def __init__(self, parent, on_need_data=None):
        super().__init__(parent, padding=20)
        self._on_need_data = on_need_data
        self._result = None

        ttk.Label(self, text="Plan your canteen visit", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w")
        self._summary = ttk.Label(self, text="No data yet.", style="Muted.TLabel", wraplength=900)
        self._summary.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 12))

        # left: best-time chart
        chart_card = ttk.Frame(self, style="Card.TFrame", padding=6)
        chart_card.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        self._figure_frame = FigureFrame(chart_card, toolbar=False)
        self._figure_frame.pack(fill="both", expand=True)

        # right: quickest counter selector
        right = ttk.Frame(self, style="Card.TFrame", padding=16)
        right.grid(row=2, column=1, sticky="nsew")
        ttk.Label(right, text="Which counter is quickest?", style="Heading.TLabel",
                  background="#FFFFFF").pack(anchor="w")
        ttk.Label(right, text="I want to eat at:", style="Card.TLabel").pack(anchor="w", pady=(10, 2))
        self._time = tk.StringVar(value="1:15 PM")
        choices = time_choices()
        self._combo = ttk.Combobox(right, textvariable=self._time, values=choices, width=12)
        self._combo.pack(anchor="w")
        self._combo.bind("<<ComboboxSelected>>", lambda _e: self.find_counter())
        ttk.Button(right, text="Find quickest counter", style="Accent.TButton",
                   command=self.find_counter).pack(anchor="w", pady=10)

        self._answer = ttk.Label(right, text="", style="Good.TLabel", wraplength=300,
                                 background="#FFFFFF")
        self._answer.pack(anchor="w", pady=(0, 6))
        self._tree = ttk.Treeview(right, height=5)
        self._tree.pack(fill="x")
        fill_tree(self._tree, ["Counter", "Expected wait", "Based on"], [])

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)
        self._figure_frame.show_message("Waiting for simulation data.")
        self._need_data_btn = None

    # ------------------------------------------------------------------ data
    def update_results(self, result: dict) -> None:
        self._result = result
        if self._need_data_btn is not None:
            self._need_data_btn.destroy()
            self._need_data_btn = None

        best = best_time(result.get("hourly"), get_open_hour(result.get("config")))
        if best:
            label, wait = best
            self._summary.configure(
                text=f"Best time to visit: {label} - expected wait about {wait:.1f} minutes.")
        else:
            self._summary.configure(text="Not enough data to suggest a best time yet.")

        df = result.get("df")
        if df is None:
            self._figure_frame.show_message("No data to chart yet.")
        else:
            try:
                self._figure_frame.show_figure(build_figure("visualization.plots", "plot_wait_by_hour", df))
            except BackendMissing as exc:
                self._figure_frame.show_message(f"Chart not ready yet.\n{exc}")
            except Exception as exc:
                self._figure_frame.show_message(f"Could not draw the chart.\n{exc}")
        self.find_counter()

    def show_no_data_hint(self) -> None:
        """Called when the student view is opened before any run."""
        if self._result is not None:
            return
        self._summary.configure(
            text="No simulation has been run yet. Ask the canteen manager to run one, "
                 "or switch to the Manager view.")
        if self._on_need_data and self._need_data_btn is None:
            self._need_data_btn = ttk.Button(self, text="Go to Manager view",
                                             command=self._on_need_data)
            self._need_data_btn.grid(row=3, column=0, sticky="w", pady=10)

    # ---------------------------------------------------------------- answer
    def find_counter(self) -> None:
        if not self._result or self._result.get("df") is None:
            self._answer.configure(text="Run a simulation first.")
            return
        try:
            clock = parse_clock(self._time.get())
        except ValueError:
            self._answer.configure(
                text="Please pick a time like 1:15 PM from the list.", style="Bad.TLabel")
            return
        open_minutes = get_open_hour(self._result.get("config")) * 60
        rows, all_day = quickest_counter(self._result["df"], clock, open_minutes)
        if not rows:
            fill_tree(self._tree, ["Counter", "Expected wait", "Based on"], [])
            self._answer.configure(text="No served customers in the data for that time.",
                                   style="Bad.TLabel")
            return
        best_name, best_wait, _ = rows[0]
        note = " (all-day average - no data near that time)" if all_day else ""
        self._answer.configure(
            text=f"Go to {best_name}: about {best_wait:.1f} min wait{note}", style="Good.TLabel")
        fill_tree(self._tree, ["Counter", "Expected wait", "Based on"],
                  [(name, f"{wait:.1f} min", f"{n} students") for name, wait, n in rows])
