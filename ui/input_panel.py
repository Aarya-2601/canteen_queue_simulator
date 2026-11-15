"""Run Simulation tab: settings form, validation, background thread (owner: Jiya).

The simulation runs in a worker thread so the window never freezes.  The worker
never touches Tkinter; it talks to the UI only through a ``queue.Queue`` that the
main thread polls with ``after()`` (viva Q5 in the README).
"""

from __future__ import annotations

import queue
import threading
import traceback
import tkinter as tk
from tkinter import messagebox, ttk

from ui.helpers import (BackendMissing, DEFAULT_SETTINGS, FIELDS, SAMPLE_CUSTOMERS_CSV,
                        load_default_settings, run_pipeline, validate_settings)


class InputPanel(ttk.Frame):
    """Settings form + Run button + progress bar."""

    def __init__(self, parent, on_complete, config_path=None, sample_csv=None, on_status=None):
        super().__init__(parent, padding=24)
        self._on_complete = on_complete
        self._config_path = config_path
        self._sample_csv = sample_csv or SAMPLE_CUSTOMERS_CSV
        self._on_status = on_status or (lambda text: None)
        self._queue: queue.Queue = queue.Queue()
        self._running = False
        self._vars: dict[str, tk.StringVar] = {}
        self._build()
        self.set_values(load_default_settings(config_path))

    # ------------------------------------------------------------------ build
    def _build(self) -> None:
        ttk.Label(self, text="Simulation settings", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(self, text="Set up the canteen, then press Run. Leave the seed as it is to "
                             "get repeatable results.", style="Muted.TLabel").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(2, 14))

        for offset, field in enumerate(FIELDS):
            row = offset + 2
            var = tk.StringVar()
            self._vars[field["key"]] = var
            ttk.Label(self, text=field["label"]).grid(row=row, column=0, sticky="w", pady=6)
            if field["kind"] is int and field["key"] != "seed":
                widget = ttk.Spinbox(self, from_=field["min"], to=field["max"],
                                     textvariable=var, width=12)
            else:
                widget = ttk.Entry(self, textvariable=var, width=14)
            widget.grid(row=row, column=1, sticky="w", padx=12)
            ttk.Label(self, text=field["hint"], style="Muted.TLabel").grid(
                row=row, column=2, sticky="w")

        buttons = ttk.Frame(self)
        buttons.grid(row=len(FIELDS) + 2, column=0, columnspan=3, sticky="w", pady=(18, 8))
        self._run_btn = ttk.Button(buttons, text="Run simulation", style="Accent.TButton",
                                   command=self.run)
        self._run_btn.pack(side="left")
        self._reset_btn = ttk.Button(buttons, text="Reset", command=self.reset)
        self._reset_btn.pack(side="left", padx=8)
        self._sample_btn = ttk.Button(buttons, text="Use sample data", command=self.run_sample)
        self._sample_btn.pack(side="left")
        if not self._sample_csv or not _exists(self._sample_csv):
            self._sample_btn.state(["disabled"])

        self._progress = ttk.Progressbar(self, mode="indeterminate", length=380)
        self._progress.grid(row=len(FIELDS) + 3, column=0, columnspan=3, sticky="w", pady=(10, 2))
        self._status = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self._status, style="Muted.TLabel").grid(
            row=len(FIELDS) + 4, column=0, columnspan=3, sticky="w")

    # ----------------------------------------------------------------- values
    def set_values(self, settings: dict) -> None:
        for key, var in self._vars.items():
            value = settings.get(key, DEFAULT_SETTINGS.get(key))
            var.set("" if value is None else str(value))

    def reset(self) -> None:
        if not self._running:
            self.set_values(load_default_settings(self._config_path))
            self._set_status("Settings reset.")

    # -------------------------------------------------------------------- run
    def run(self) -> None:
        if self._running:
            return
        settings, errors = validate_settings({k: v.get() for k, v in self._vars.items()})
        if errors:
            messagebox.showerror(
                "Please check your inputs",
                "Some settings need fixing before the simulation can run:\n\n"
                + "\n".join(f"  • {e}" for e in errors))
            return
        self._start(settings, sample=False)

    def run_sample(self) -> None:
        if self._running:
            return
        settings, errors = validate_settings({k: v.get() for k, v in self._vars.items()})
        if errors:  # sample mode still needs sensible settings for the config
            settings = dict(DEFAULT_SETTINGS)
        self._start(settings, sample=True)

    def _start(self, settings: dict, sample: bool) -> None:
        self._running = True
        self._set_buttons(False)
        self._progress.start(12)
        self._set_status("Starting...")
        thread = threading.Thread(target=self._worker, args=(settings, sample), daemon=True)
        thread.start()
        self.after(100, self._poll)

    def _worker(self, settings: dict, sample: bool) -> None:
        """Runs in the background thread - must not touch any Tk widget."""
        try:
            result = run_pipeline(
                settings, config_path=self._config_path,
                sample_csv=str(self._sample_csv) if sample else None,
                progress=lambda text: self._queue.put(("progress", text)))
            self._queue.put(("done", result))
        except Exception as exc:  # delivered to the main thread, never crashes the app
            traceback.print_exc()
            self._queue.put(("error", exc))

    def _poll(self) -> None:
        """Runs in the main thread: collect messages from the worker."""
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "progress":
                    self._set_status(payload)
                elif kind == "done":
                    self._finish("Done.")
                    self._on_complete(payload)
                    return
                elif kind == "error":
                    self._finish("Stopped.")
                    self._show_error(payload)
                    return
        except queue.Empty:
            pass
        if self._running:
            self.after(100, self._poll)

    def _finish(self, status: str) -> None:
        self._running = False
        self._progress.stop()
        self._set_buttons(True)
        self._set_status(status)

    def _show_error(self, exc: Exception) -> None:
        if isinstance(exc, BackendMissing):
            messagebox.showwarning("Part of the project is missing", str(exc))
        elif isinstance(exc, FileNotFoundError):
            messagebox.showerror("File not found",
                                 f"A required file could not be found:\n{exc}")
        else:
            messagebox.showerror(
                "Simulation problem",
                "Something went wrong while running the simulation:\n\n"
                f"{exc}\n\nYour settings are unchanged - adjust them and try again.")

    # ---------------------------------------------------------------- helpers
    def _set_buttons(self, enabled: bool) -> None:
        for btn in (self._run_btn, self._reset_btn):
            btn.state(["!disabled"] if enabled else ["disabled"])
        if _exists(self._sample_csv):
            self._sample_btn.state(["!disabled"] if enabled else ["disabled"])

    def _set_status(self, text: str) -> None:
        self._status.set(text)
        self._on_status(text)


def _exists(path) -> bool:
    from pathlib import Path
    return Path(str(path)).is_file()
