"""Charts tab + reusable figure-embedding widget (owner: Jiya).

Chaiti's plot functions return ``matplotlib.figure.Figure`` objects (README
section 4, "UI Rules").  ``FigureFrame`` embeds such a figure with
``FigureCanvasTkAgg``; ``ChartsPanel`` adds a chart picker and a Save button.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib

matplotlib.use("TkAgg")  # must be chosen before any figure is created
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # noqa: E402
from matplotlib import pyplot as plt  # noqa: E402

from ui.helpers import BackendMissing, OUTPUT_CHARTS_DIR, import_backend  # noqa: E402
from ui.styles import PALETTE, FONTS  # noqa: E402

# label shown in the picker -> (module, function, which result entry it needs)
CHART_CHOICES = {
    "Wait by hour": ("visualization.plots", "plot_wait_by_hour", "df"),
    "Queue length over time": ("visualization.plots", "plot_queue_lengths", "df"),
    "Counter utilisation": ("visualization.plots", "plot_utilisation", "df"),
    "Wait time histogram": ("visualization.plots", "plot_wait_histogram", "df"),
    "Dashboard (2 x 2)": ("visualization.dashboard", "plot_dashboard", "df"),
    "Scenario comparison": ("visualization.plots", "plot_scenario_comparison", "comparison"),
}


def build_figure(module: str, func_name: str, data):
    """Call one of Chaiti's plot functions; raises ``BackendMissing`` if absent."""
    func = import_backend(module, func_name)
    return func(data)


class FigureFrame(ttk.Frame):
    """A frame that can show a Matplotlib ``Figure`` (or a short message)."""

    def __init__(self, parent, toolbar: bool = True):
        super().__init__(parent)
        self._with_toolbar = toolbar
        self._figure = None
        self._canvas = None
        self.show_message("Nothing to show yet.")

    @property
    def figure(self):
        return self._figure

    def clear(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        if self._figure is not None:
            try:
                plt.close(self._figure)
            except Exception:
                pass
        self._figure = None
        self._canvas = None

    def show_message(self, text: str) -> None:
        self.clear()
        label = ttk.Label(self, text=text, style="Muted.TLabel", wraplength=420,
                          justify="center", anchor="center")
        label.pack(expand=True, fill="both", padx=20, pady=40)

    def show_figure(self, figure) -> None:
        self.clear()
        self._figure = figure
        if self._with_toolbar:
            bar_holder = ttk.Frame(self)
            bar_holder.pack(side="bottom", fill="x")
        self._canvas = FigureCanvasTkAgg(figure, master=self)
        if self._with_toolbar:
            toolbar = NavigationToolbar2Tk(self._canvas, bar_holder, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side="left")
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(side="top", fill="both", expand=True)


class ChartsPanel(ttk.Frame):
    """Charts tab: pick a chart, see it embedded, save it as PNG."""

    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self._result = None

        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Label(bar, text="Chart:", style="Heading.TLabel").pack(side="left")
        self._choice = tk.StringVar(value=next(iter(CHART_CHOICES)))
        picker = ttk.Combobox(bar, textvariable=self._choice, state="readonly",
                              values=list(CHART_CHOICES), width=28)
        picker.pack(side="left", padx=8)
        picker.bind("<<ComboboxSelected>>", lambda _e: self.render())
        self._save_btn = ttk.Button(bar, text="Save chart...", command=self.save_chart)
        self._save_btn.pack(side="right")

        card = ttk.Frame(self, style="Card.TFrame", padding=6)
        card.pack(fill="both", expand=True)
        self._figure_frame = FigureFrame(card)
        self._figure_frame.pack(fill="both", expand=True)
        self._figure_frame.show_message("Run a simulation to see charts here.")

    def update_results(self, result: dict) -> None:
        self._result = result
        self.render()

    def render(self) -> None:
        if not self._result:
            return
        module, func_name, needs = CHART_CHOICES[self._choice.get()]
        data = self._result.get(needs)
        if data is None:
            reason = self._result.get("scenario_error") or "No data for this chart yet."
            self._figure_frame.show_message(f"This chart is not available.\n{reason}")
            return
        try:
            figure = build_figure(module, func_name, data)
            self._figure_frame.show_figure(figure)
        except BackendMissing as exc:
            self._figure_frame.show_message(f"Chart not ready yet.\n{exc}")
        except Exception as exc:  # a bug in a plot function must not crash the app
            self._figure_frame.show_message(f"Could not draw this chart.\n{exc}")

    def save_chart(self) -> None:
        figure = self._figure_frame.figure
        if figure is None:
            messagebox.showinfo("Save chart", "There is no chart to save yet.")
            return
        OUTPUT_CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        default = self._choice.get().lower().replace(" ", "_").replace("(", "").replace(")", "")
        path = filedialog.asksaveasfilename(
            title="Save chart", defaultextension=".png",
            initialdir=str(OUTPUT_CHARTS_DIR), initialfile=f"{default}.png",
            filetypes=[("PNG image", "*.png"), ("PDF", "*.pdf")])
        if not path:
            return
        try:
            figure.savefig(path, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Save chart", f"Chart saved to:\n{path}")
        except (OSError, PermissionError) as exc:
            messagebox.showerror("Save chart", f"Could not save the chart.\n{exc}")
