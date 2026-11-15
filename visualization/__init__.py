"""
visualization package
Owner: Chaiti

Exports plotting functions and dashboard generators for the VJTI Canteen Queue Simulator:
- plot_wait_by_hour(df)
- plot_queue_lengths(df)
- plot_utilisation(df)
- plot_wait_histogram(df)
- plot_scenario_comparison(comparison_df)
- plot_dashboard(df)
"""

from visualization.plots import (
    plot_wait_by_hour,
    plot_queue_lengths,
    plot_utilisation,
    plot_wait_histogram,
    plot_scenario_comparison,
)
from visualization.dashboard import plot_dashboard

__all__ = [
    "plot_wait_by_hour",
    "plot_queue_lengths",
    "plot_utilisation",
    "plot_wait_histogram",
    "plot_scenario_comparison",
    "plot_dashboard",
]
