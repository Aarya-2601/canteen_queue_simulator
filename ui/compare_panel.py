"""Compare Scenarios tab: comparison table, recommendation text, chart (owner: Jiya)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.charts_panel import FigureFrame, build_figure
from ui.helpers import BackendMissing, dataframe_to_rows
from ui.results_panel import fill_tree


class ComparePanel(ttk.Frame):
    """Shows Janhavi's comparison table (with % improvement) and recommendation."""

    def __init__(self, parent):
        super().__init__(parent, padding=16)

        ttk.Label(self, text="Scenario comparison", style="Heading.TLabel").pack(anchor="w")
        self._note = ttk.Label(self, text="Run a simulation to compare the what-if scenarios.",
                               style="Muted.TLabel")
        self._note.pack(anchor="w", pady=(2, 8))

        holder = ttk.Frame(self)
        holder.pack(fill="x")
        self._tree = ttk.Treeview(holder, height=5)
        xscroll = ttk.Scrollbar(holder, orient="horizontal", command=self._tree.xview)
        self._tree.configure(xscrollcommand=xscroll.set)
        self._tree.pack(fill="x")
        xscroll.pack(fill="x")

        box = ttk.LabelFrame(self, text="Recommendation", padding=8)
        box.pack(fill="x", pady=10)
        self._text = tk.Text(box, height=6, wrap="word", font=("Segoe UI", 10),
                             relief="flat", state="disabled")
        self._text.pack(fill="x")

        card = ttk.Frame(self, style="Card.TFrame", padding=6)
        card.pack(fill="both", expand=True)
        self._figure_frame = FigureFrame(card, toolbar=False)
        self._figure_frame.pack(fill="both", expand=True)
        self._figure_frame.show_message("The comparison chart appears here after a run.")

    def _set_text(self, text: str) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.insert("1.0", text)
        self._text.configure(state="disabled")

    def update_results(self, result: dict) -> None:
        comparison = result.get("comparison")
        if comparison is None:
            fill_tree(self._tree, [], [])
            reason = result.get("scenario_error") or "No scenario results yet."
            self._note.configure(text="Scenario comparison is not available.")
            self._set_text(reason)
            self._figure_frame.show_message(reason)
            return

        columns, rows = dataframe_to_rows(comparison)
        fill_tree(self._tree, columns, rows, min_width=110)
        self._note.configure(text="Each row is a what-if scenario; improvement is measured "
                                  "against the current setup.")
        self._set_text(result.get("recommendation") or "No recommendation was produced.")
        try:
            figure = build_figure("visualization.plots", "plot_scenario_comparison", comparison)
            self._figure_frame.show_figure(figure)
        except BackendMissing as exc:
            self._figure_frame.show_message(f"Chart not ready yet.\n{exc}")
        except Exception as exc:
            self._figure_frame.show_message(f"Could not draw the comparison chart.\n{exc}")
