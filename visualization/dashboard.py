"""
visualization/dashboard.py - 2x2 multi-panel executive dashboard.
Owner: Chaiti
"""

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from visualization.plots import C_NAVY, C_ORANGE, C_RED, PALETTE


def plot_dashboard(df: pd.DataFrame) -> Figure:
    """Constructs a 2x2 summary dashboard figure."""
    fig = Figure(figsize=(10, 7.5), dpi=100)
    fig.suptitle("VJTI Canteen Queue Simulator — Dashboard", fontsize=14, fontweight="bold", color=C_NAVY)

    ax1 = fig.add_subplot(221)  # Hourly waits
    ax2 = fig.add_subplot(222)  # Queue timeline
    ax3 = fig.add_subplot(223)  # Wait distribution
    ax4 = fig.add_subplot(224)  # Counter utilisation

    if df is None or df.empty or "wait_time" not in df.columns:
        for ax in [ax1, ax2, ax3, ax4]:
            ax.text(0.5, 0.5, "No Data", ha="center", va="center")
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        return fig

    served = df[df["balked"] == False].copy()

    # 1. Hourly waits
    if not served.empty:
        served["hour"] = served["arrival_time"] // 60
        grp = served.groupby("hour")["wait_time"].agg(
            avg="mean", p90=lambda s: np.percentile(s.dropna(), 90) if len(s.dropna()) else 0
        ).reset_index()
        x = np.arange(len(grp))
        w = 0.35
        ax1.bar(x - w / 2, grp["avg"], w, label="Avg", color=C_NAVY)
        ax1.bar(x + w / 2, grp["p90"], w, label="P90", color=C_ORANGE)
        ax1.set_xticks(x)
        ax1.set_xticklabels([f"{10 + int(h)}:00" for h in grp["hour"]], fontsize=8)
        ax1.set_title("Hourly Wait Times", fontsize=10, fontweight="bold")
        ax1.legend(fontsize=8)
        ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # 2. Queue timeline
    if "counter" in df.columns:
        for i, c in enumerate(sorted(df["counter"].unique())):
            c_df = df[df["counter"] == c].copy()
            c_df["bin"] = (c_df["arrival_time"] // 5) * 5
            binned = c_df.groupby("bin")["queue_length_on_arrival"].mean().reset_index()
            ax2.plot(binned["bin"], binned["queue_length_on_arrival"], label=c,
                     color=PALETTE[i % len(PALETTE)], linewidth=1.5)
        ax2.axvspan(150, 240, color="#FFECB3", alpha=0.4, label="Lunch")
        ax2.set_title("Queue Lengths Over Time", fontsize=10, fontweight="bold")
        ax2.legend(fontsize=8)
        ax2.grid(True, linestyle="--", alpha=0.5)

    # 3. Wait distribution
    if not served.empty:
        w_data = served["wait_time"].dropna()
        ax3.hist(w_data, bins=12, color=C_NAVY, edgecolor="white", alpha=0.85)
        ax3.axvline(np.percentile(w_data, 90), color=C_RED, linestyle="--", label="P90")
        ax3.set_title("Wait Time Distribution", fontsize=10, fontweight="bold")
        ax3.legend(fontsize=8)
        ax3.grid(axis="y", linestyle="--", alpha=0.5)

    # 4. Utilisation
    if "counter" in df.columns and "service_time" in df.columns:
        tot = served.groupby("counter")["service_time"].sum()
        total_time = max(360.0, df["arrival_time"].max() if not df.empty else 360.0)
        staff_map = {"Snacks": 2, "Thali": 2, "Beverages": 1}
        names = list(tot.index)
        rates = [min(100.0, (tot[n] / (total_time * staff_map.get(n, 1))) * 100.0) for n in names]
        y = np.arange(len(names))
        ax4.barh(y, rates, color=C_NAVY, height=0.45)
        ax4.set_yticks(y)
        ax4.set_yticklabels(names, fontsize=8)
        ax4.set_title("Counter Utilisation (%)", fontsize=10, fontweight="bold")
        ax4.grid(axis="x", linestyle="--", alpha=0.5)

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    return fig
