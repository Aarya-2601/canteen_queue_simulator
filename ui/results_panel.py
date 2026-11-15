"""Results tab (KPI cards + per-counter table) and Reports tab (owner: Jiya)."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from ui.helpers import (OUTPUT_REPORTS_DIR, BackendMissing, counter_rows, get_open_hour,
                        import_backend, kpi_items, peak_queue_text)


def fill_tree(tree: ttk.Treeview, columns: list[str], rows: list, min_width: int = 90) -> None:
    """Replace the contents (and columns) of a Treeview."""
    tree.delete(*tree.get_children())
    tree["columns"] = columns
    tree["show"] = "headings"
    for name in columns:
        tree.heading(name, text=name)
        tree.column(name, width=max(min_width, len(name) * 10), anchor="center", stretch=True)
    for row in rows:
        tree.insert("", "end", values=list(row))


class ResultsPanel(ttk.Frame):
    """KPI cards and a table with one row per counter."""

    def __init__(self, parent):
        super().__init__(parent, padding=16)
        self._kpi_labels: dict[str, ttk.Label] = {}

        self._source = ttk.Label(self, text="Run a simulation to see the results here.",
                                 style="Muted.TLabel")
        self._source.pack(anchor="w", pady=(0, 8))

        cards = ttk.Frame(self)
        cards.pack(fill="x")
        for col, item in enumerate(kpi_items(None)):
            card = ttk.Frame(cards, style="Card.TFrame", padding=(14, 12))
            card.grid(row=0, column=col, padx=6, sticky="nsew")
            cards.columnconfigure(col, weight=1)
            value = ttk.Label(card, text=item["value"], style="KpiValue.TLabel")
            value.pack(anchor="w")
            ttk.Label(card, text=item["label"], style="KpiLabel.TLabel").pack(anchor="w")
            self._kpi_labels[item["key"]] = value

        self._peak = ttk.Label(self, text="", style="Muted.TLabel")
        self._peak.pack(anchor="w", pady=(10, 4))

        ttk.Label(self, text="Per-counter summary", style="Heading.TLabel").pack(anchor="w", pady=(8, 4))
        holder = ttk.Frame(self)
        holder.pack(fill="both", expand=True)
        self._tree = ttk.Treeview(holder, height=8)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        fill_tree(self._tree, ["Counter", "Utilisation", "Revenue"], [])

    def update_results(self, result: dict) -> None:
        metrics = result.get("metrics") or {}
        for item in kpi_items(metrics):
            self._kpi_labels[item["key"]].configure(text=item["value"])
        self._peak.configure(text=peak_queue_text(metrics, get_open_hour(result.get("config"))))
        fill_tree(self._tree, ["Counter", "Utilisation", "Revenue"], counter_rows(metrics))

        if result.get("source") == "sample":
            self._source.configure(text="Showing: sample data (tests/dummy_customers.csv)")
        else:
            seed = (result.get("settings") or {}).get("seed")
            self._source.configure(
                text="Showing: latest simulation" + (f" (seed {seed})" if seed is not None else ""))


class ReportsPanel(ttk.Frame):
    """Save the text report / raw CSV and open the reports folder."""

    def __init__(self, parent):
        super().__init__(parent, padding=24)
        self._result = None

        ttk.Label(self, text="Reports", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(self, text="Save the results of the latest run, or open the folder where "
                             "reports are kept.", style="Muted.TLabel").pack(anchor="w", pady=(2, 14))

        row = ttk.Frame(self)
        row.pack(anchor="w")
        ttk.Button(row, text="Save report (TXT)...", command=self.save_text_report).pack(side="left")
        ttk.Button(row, text="Save customer data (CSV)...", command=self.save_csv).pack(side="left", padx=8)
        ttk.Button(row, text="Open reports folder", command=self.open_folder).pack(side="left")

        self._status = ttk.Label(self, text="", style="Muted.TLabel", wraplength=600)
        self._status.pack(anchor="w", pady=14)

    def set_result(self, result: dict) -> None:
        self._result = result
        self._status.configure(text="Latest results are ready to save.")

    def _need_result(self) -> bool:
        if not self._result:
            messagebox.showinfo("Reports", "Run a simulation first, then save its report.")
            return False
        return True

    @staticmethod
    def _stamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_text_report(self) -> None:
        if not self._need_result():
            return
        OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = filedialog.asksaveasfilename(
            title="Save report", defaultextension=".txt", initialdir=str(OUTPUT_REPORTS_DIR),
            initialfile=f"canteen_report_{self._stamp()}.txt",
            filetypes=[("Text report", "*.txt")])
        if not path:
            return
        try:
            save_report = import_backend("analysis.report_generator", "save_report")
            saved = save_report(self._result["df"], self._result["metrics"], path)
            self._status.configure(text=f"Report saved: {saved or path}")
        except BackendMissing as exc:
            messagebox.showwarning("Report not ready yet", str(exc))
        except (OSError, PermissionError) as exc:
            messagebox.showerror("Save report", f"Could not save the report.\n{exc}")
        except Exception as exc:
            messagebox.showerror("Save report", f"Something went wrong while saving.\n{exc}")

    def save_csv(self) -> None:
        if not self._need_result():
            return
        OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = filedialog.asksaveasfilename(
            title="Save customer data", defaultextension=".csv", initialdir=str(OUTPUT_REPORTS_DIR),
            initialfile=f"customers_{self._stamp()}.csv", filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        try:
            self._result["df"].to_csv(path, index=False)
            self._status.configure(text=f"Customer data saved: {path}")
        except (OSError, PermissionError) as exc:
            messagebox.showerror("Save data", f"Could not save the file.\n{exc}")

    def open_folder(self) -> None:
        OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = str(OUTPUT_REPORTS_DIR)
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as exc:
            messagebox.showinfo("Reports folder", f"Reports are saved in:\n{path}\n\n({exc})")
