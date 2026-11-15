"""
visualization/plots.py - Individual Matplotlib charts for VJTI Canteen.
Owner: Chaiti
"""

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

# Clean styling colors
C_NAVY = "#003366"
C_ORANGE = "#E65100"
C_TEAL = "#00897B"
C_RED = "#C62828"
PALETTE = ["#003366", "#00897B", "#E65100", "#7B1FA2"]


def plot_wait_by_hour(df: pd.DataFrame) -> Figure:
    """Hourly Average and P90 wait time bar chart."""
    fig = Figure(figsize=(7, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    served = df[df["balked"] == False].copy() if df is not None and not df.empty else pd.DataFrame()
    if served.empty:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    served["hour"] = served["arrival_time"] // 60
    grouped = served.groupby("hour")["wait_time"].agg(
        avg="mean",
        p90=lambda s: np.percentile(s.dropna(), 90) if len(s.dropna()) > 0 else 0.0
    ).reset_index()

    labels = [f"{10 + int(h)}:00" for h in grouped["hour"]]
    x = np.arange(len(labels))
    w = 0.35

    ax.bar(x - w / 2, grouped["avg"], w, label="Avg Wait", color=C_NAVY)
    ax.bar(x + w / 2, grouped["p90"], w, label="P90 Wait", color=C_ORANGE)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Wait Time (min)")
    ax.set_title("Hourly Wait Times (Avg vs P90)", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_queue_lengths(df: pd.DataFrame) -> Figure:
    """Timeline of queue lengths across counters."""
    fig = Figure(figsize=(7, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    if df is None or df.empty or "counter" not in df.columns:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    for idx, c_name in enumerate(sorted(df["counter"].unique())):
        c_df = df[df["counter"] == c_name].copy()
        c_df["bin"] = (c_df["arrival_time"] // 5) * 5
        binned = c_df.groupby("bin")["queue_length_on_arrival"].mean().reset_index()
        ax.plot(binned["bin"], binned["queue_length_on_arrival"], label=c_name,
                color=PALETTE[idx % len(PALETTE)], linewidth=1.8)

    ax.axvspan(150, 240, color="#FFECB3", alpha=0.45, label="Lunch Rush")
    ax.set_xlabel("Simulation Minute")
    ax.set_ylabel("Queue Length")
    ax.set_title("Queue Length Timeline", fontweight="bold")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_utilisation(df: pd.DataFrame) -> Figure:
    """Counter staff utilisation rates horizontal bar chart."""
    fig = Figure(figsize=(7, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    if df is None or df.empty or "counter" not in df.columns:
        ax.text(0.5, 0.5, "No Data Available", ha="center", va="center")
        return fig

    served = df[df["balked"] == False]
    total_time = max(360.0, df["arrival_time"].max() if not df.empty else 360.0)
    totals = served.groupby("counter")["service_time"].sum()
    staff_map = {"Snacks": 2, "Thali": 2, "Beverages": 1}

    names = list(totals.index)
    rates = [min(100.0, round((totals[n] / (total_time * staff_map.get(n, 1))) * 100.0, 1)) for n in names]

    y = np.arange(len(names))
    ax.barh(y, rates, color=C_NAVY, height=0.5)
    ax.axvline(80.0, color=C_RED, linestyle="--", label="High Load (80%)")
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Utilisation (%)")
    ax.set_title("Counter Staff Utilisation", fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_wait_histogram(df: pd.DataFrame) -> Figure:
    """Frequency histogram of student wait times."""
    fig = Figure(figsize=(7, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    served = df[df["balked"] == False]["wait_time"].dropna() if df is not None and not df.empty else []
    if len(served) == 0:
        ax.text(0.5, 0.5, "No Wait Times Recorded", ha="center", va="center")
        return fig

    p90 = float(np.percentile(served, 90))
    median = float(np.median(served))

    ax.hist(served, bins=15, color=C_NAVY, edgecolor="white", alpha=0.85)
    ax.axvline(median, color="#FFA000", linestyle="-.", linewidth=2, label=f"Median ({median:.1f}m)")
    ax.axvline(p90, color=C_RED, linestyle="--", linewidth=2, label=f"P90 ({p90:.1f}m)")
    ax.set_xlabel("Wait Time (min)")
    ax.set_ylabel("Number of Students")
    ax.set_title("Wait Time Distribution", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_scenario_comparison(comparison_df: pd.DataFrame) -> Figure:
    """Bar chart comparing operational scenarios."""
    fig = Figure(figsize=(7.5, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    if comparison_df is None or comparison_df.empty:
        ax.text(0.5, 0.5, "No Scenario Data", ha="center", va="center")
        return fig

    scenarios = comparison_df["scenario"].tolist() if "scenario" in comparison_df.columns else comparison_df.index.tolist()
    avg_waits = comparison_df["avg_wait"].tolist() if "avg_wait" in comparison_df.columns else [5.0] * len(scenarios)
    balk_rates = comparison_df["balking_rate"].tolist() if "balking_rate" in comparison_df.columns else [10.0] * len(scenarios)

    x = np.arange(len(scenarios))
    w = 0.35
    ax.bar(x - w / 2, avg_waits, w, label="Avg Wait (min)", color=C_NAVY)
    ax.bar(x + w / 2, balk_rates, w, label="Balking %", color=C_ORANGE)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=15, ha="right")
    ax.set_title("Scenario Comparison", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig
