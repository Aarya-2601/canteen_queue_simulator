"""Pure-Python helpers for the desktop app (owner: Jiya).

Nothing in this module imports Tkinter, so it can be unit-tested anywhere
(see ``tests/test_ui_helpers.py``).  It holds:

* input validation for the settings form,
* the *only* place that knows how form values map onto the config dict,
* formatting helpers for KPI cards / tables,
* the Student-view logic (best time, quickest counter),
* ``run_pipeline`` - the glue that calls Aarya's, Chaiti's and Janhavi's
  functions exactly as listed in the README interface contract (section 7.2).
"""

from __future__ import annotations

import copy
import importlib
import math
import re
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "canteen_config.json"
SAMPLE_CUSTOMERS_CSV = PROJECT_ROOT / "tests" / "dummy_customers.csv"
OUTPUT_CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"

# --------------------------------------------------------------------------- #
# ASSUMPTIONS ABOUT THE CONFIG FILE  (confirm with Chaiti, edit ONLY here)
# --------------------------------------------------------------------------- #
CONFIG_KEYS = {
    "counters": "counters",              # list of counter dicts (or names)
    "counter_name": "name",              # key inside each counter dict
    "counter_staff": "staff",            # key inside each counter dict
    "peak_rate": "peak_arrival_rate",    # students per minute at the lunch peak
    "balking_limit": "balking_limit",    # queue length at which people leave
}
OPEN_HOUR_KEYS = ("open_hour", "opening_hour")   # hour (0-23) the canteen opens
DEFAULT_OPEN_HOUR = 9

# --------------------------------------------------------------------------- #
# Settings form
# --------------------------------------------------------------------------- #
FIELDS: list[dict[str, Any]] = [
    {"key": "num_counters", "label": "Number of counters", "kind": int,
     "min": 1, "max": 10, "default": 3, "required": True,
     "hint": "whole number, 1 to 10"},
    {"key": "staff_per_counter", "label": "Staff per counter", "kind": int,
     "min": 1, "max": 10, "default": 2, "required": True,
     "hint": "whole number, 1 to 10"},
    {"key": "peak_arrival_rate", "label": "Peak arrival rate (students/min)",
     "kind": float, "min": 0.1, "max": 100.0, "default": 6.0, "required": True,
     "hint": "e.g. 6 or 7.5"},
    {"key": "balking_limit", "label": "Balking limit (queue length)", "kind": int,
     "min": 1, "max": 100, "default": 12, "required": True,
     "hint": "students in a queue before others walk away"},
    {"key": "seed", "label": "Random seed (optional)", "kind": int,
     "min": 0, "max": 2**31 - 1, "default": 42, "required": False,
     "hint": "same seed = same results; leave empty for random"},
]

DEFAULT_SETTINGS = {f["key"]: f["default"] for f in FIELDS}


class BackendMissing(RuntimeError):
    """A teammate's module/function is not available yet (not merged, renamed...)."""


def _parse_number(text: str, kind: type):
    text = text.strip()
    if kind is int:
        if not re.fullmatch(r"[+-]?\d+", text):
            raise ValueError
        return int(text)
    value = float(text)
    if not math.isfinite(value):
        raise ValueError
    return value


def validate_settings(raw: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Check the form values.

    ``raw`` maps field keys to whatever the user typed (strings).  Returns
    ``(clean_settings, errors)``; when ``errors`` is non-empty the caller shows
    them in a messagebox instead of running.  Never raises on bad input.
    """
    clean: dict[str, Any] = {}
    errors: list[str] = []
    for field in FIELDS:
        key, label, kind = field["key"], field["label"], field["kind"]
        text = str(raw.get(key, "") if raw.get(key, "") is not None else "").strip()
        if text == "":
            if field["required"]:
                errors.append(f"{label} is empty - please enter a value ({field['hint']}).")
            else:
                clean[key] = None
            continue
        try:
            value = _parse_number(text, kind)
        except ValueError:
            what = "a whole number" if kind is int else "a number"
            errors.append(f"{label} must be {what} ({field['hint']}); you typed '{text}'.")
            continue
        if value < field["min"] or value > field["max"]:
            errors.append(
                f"{label} must be between {field['min']} and {field['max']}; you typed {text}."
            )
            continue
        clean[key] = value
    return clean, errors


def apply_settings_to_config(config: dict, settings: dict) -> dict:
    """Return a COPY of ``config`` with the form values applied.

    This is the only function that knows the config's key names
    (see ``CONFIG_KEYS`` above).
    """
    cfg = copy.deepcopy(config) if config else {}
    ck = CONFIG_KEYS

    counters = cfg.get(ck["counters"])
    if isinstance(counters, list) and counters:
        wanted = int(settings["num_counters"])
        counters = counters[:wanted]
        while len(counters) < wanted:
            template = copy.deepcopy(counters[-1])
            label = f"Counter {len(counters) + 1}"
            if isinstance(template, dict):
                template[ck["counter_name"]] = label
                counters.append(template)
            else:
                counters.append(label)
        for counter in counters:
            if isinstance(counter, dict):
                counter[ck["counter_staff"]] = int(settings["staff_per_counter"])
        cfg[ck["counters"]] = counters

    cfg[ck["peak_rate"]] = float(settings["peak_arrival_rate"])
    cfg[ck["balking_limit"]] = int(settings["balking_limit"])
    return cfg


def defaults_from_config(config: dict) -> dict:
    """Form defaults taken from the loaded config (falls back to ``DEFAULT_SETTINGS``)."""
    out = dict(DEFAULT_SETTINGS)
    if not isinstance(config, dict):
        return out
    ck = CONFIG_KEYS
    counters = config.get(ck["counters"])
    if isinstance(counters, list) and counters:
        out["num_counters"] = len(counters)
        first = counters[0]
        if isinstance(first, dict) and isinstance(first.get(ck["counter_staff"]), int):
            out["staff_per_counter"] = first[ck["counter_staff"]]
    if isinstance(config.get(ck["peak_rate"]), (int, float)):
        out["peak_arrival_rate"] = config[ck["peak_rate"]]
    if isinstance(config.get(ck["balking_limit"]), int):
        out["balking_limit"] = config[ck["balking_limit"]]
    return out


def get_open_hour(config: Optional[dict]) -> int:
    """Hour of day (0-23) at which simulated minute 0 happens."""
    if isinstance(config, dict):
        for key in OPEN_HOUR_KEYS:
            value = config.get(key)
            if isinstance(value, (int, float)) and 0 <= value < 24:
                return int(value)
    return DEFAULT_OPEN_HOUR


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def fmt_minutes(value: Any) -> str:
    return "—" if _is_missing(value) else f"{float(value):.1f} min"


def fmt_percent(value: Any) -> str:
    return "—" if _is_missing(value) else f"{float(value):.1f}%"


def fmt_rupees(value: Any) -> str:
    return "—" if _is_missing(value) else f"₹{float(value):,.0f}"


def fmt_number(value: Any, decimals: int = 1) -> str:
    return "—" if _is_missing(value) else f"{float(value):,.{decimals}f}"


def minutes_to_clock(total_minutes: float) -> str:
    """Minutes since midnight -> '1:15 PM'."""
    total = int(round(total_minutes)) % (24 * 60)
    hour24, minute = divmod(total, 60)
    suffix = "AM" if hour24 < 12 else "PM"
    hour12 = hour24 % 12 or 12
    return f"{hour12}:{minute:02d} {suffix}"


def parse_clock(text: str) -> int:
    """'1:15 PM' / '13:15' -> minutes since midnight.  Raises ValueError if invalid."""
    match = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*([AaPp][Mm])?\s*", text or "")
    if not match:
        raise ValueError(f"'{text}' is not a time like 1:15 PM")
    hour, minute, suffix = int(match.group(1)), int(match.group(2)), match.group(3)
    if minute > 59:
        raise ValueError(f"'{text}' has invalid minutes")
    if suffix:
        if not 1 <= hour <= 12:
            raise ValueError(f"'{text}' has invalid hour")
        hour = hour % 12 + (12 if suffix.lower() == "pm" else 0)
    elif hour > 23:
        raise ValueError(f"'{text}' has invalid hour")
    return hour * 60 + minute


def time_choices(start_hour: int = 11, end_hour: int = 16, step: int = 15) -> list[str]:
    """Clock strings for the Student view drop-down."""
    return [minutes_to_clock(m) for m in range(start_hour * 60, end_hour * 60 + 1, step)]


def kpi_items(metrics: Optional[dict]) -> list[dict[str, str]]:
    """The five KPI cards, in display order."""
    m = metrics or {}
    return [
        {"key": "avg_wait", "label": "Average wait", "value": fmt_minutes(m.get("avg_wait"))},
        {"key": "p90_wait", "label": "90th percentile wait", "value": fmt_minutes(m.get("p90_wait"))},
        {"key": "balking_rate", "label": "Balking rate", "value": fmt_percent(m.get("balking_rate"))},
        {"key": "throughput_per_hour", "label": "Throughput / hour",
         "value": fmt_number(m.get("throughput_per_hour"), 0)},
        {"key": "total_revenue", "label": "Total revenue", "value": fmt_rupees(m.get("total_revenue"))},
    ]


def peak_queue_text(metrics: Optional[dict], open_hour: int = DEFAULT_OPEN_HOUR) -> str:
    m = metrics or {}
    peak, when = m.get("peak_queue"), m.get("peak_queue_time")
    if _is_missing(peak):
        return ""
    text = f"Peak queue: {int(peak)} students"
    if not _is_missing(when):
        text += f" at {minutes_to_clock(open_hour * 60 + float(when))}"
    return text


def counter_rows(metrics: Optional[dict]) -> list[tuple[str, str, str]]:
    """(counter, utilisation, revenue) rows for the per-counter table."""
    m = metrics or {}
    util = m.get("utilisation") or {}
    revenue = m.get("revenue_by_counter") or {}
    names = list(util.keys()) + [n for n in revenue if n not in util]
    return [(str(n), fmt_percent(util.get(n)), fmt_rupees(revenue.get(n))) for n in names]


def dataframe_to_rows(df: Optional[pd.DataFrame], decimals: int = 2) -> tuple[list[str], list[list[str]]]:
    """Turn any DataFrame into (column names, rows of strings) for a Treeview."""
    if df is None or len(df.columns) == 0:
        return [], []
    frame = df.reset_index() if not isinstance(df.index, pd.RangeIndex) else df
    columns = [str(c) for c in frame.columns]
    rows: list[list[str]] = []
    for record in frame.itertuples(index=False):
        row = []
        for value in record:
            if _is_missing(value) or (not isinstance(value, str) and pd.isna(value)):
                row.append("—")
            elif isinstance(value, float):
                row.append(f"{value:.{decimals}f}")
            else:
                row.append(str(value))
        rows.append(row)
    return columns, rows


# --------------------------------------------------------------------------- #
# Student view logic
# --------------------------------------------------------------------------- #
_HOUR_COLS = ("hour", "hour_of_day", "hour_label", "slot", "time")
_AVG_COLS = ("avg_wait", "mean_wait", "average_wait", "avg_wait_time", "wait_mean", "mean")


def _find_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> Optional[str]:
    lowered = {str(c).lower(): c for c in df.columns}
    for name in candidates:
        if name in lowered:
            return lowered[name]
    return None


def best_time(hourly: Optional[pd.DataFrame]) -> Optional[tuple[str, float]]:
    """(label, average wait) of the hour with the shortest average wait."""
    if hourly is None or len(hourly) == 0:
        return None
    frame = hourly.reset_index() if not isinstance(hourly.index, pd.RangeIndex) else hourly
    avg_col = _find_column(frame, _AVG_COLS)
    if avg_col is None:
        numeric = [c for c in frame.columns if pd.api.types.is_numeric_dtype(frame[c])]
        avg_col = numeric[-1] if numeric else None
    if avg_col is None:
        return None
    hour_col = _find_column(frame, _HOUR_COLS) or frame.columns[0]
    valid = frame[[hour_col, avg_col]].dropna()
    if valid.empty:
        return None
    best_index = valid[avg_col].idxmin()
    # read the two cells separately so an integer hour is not upcast to 14.0
    return str(valid.at[best_index, hour_col]), float(valid.at[best_index, avg_col])


def quickest_counter(df: Optional[pd.DataFrame], clock_minutes: int, open_minutes: int,
                     window: int = 15) -> tuple[list[tuple[str, float, int]], bool]:
    """Rank counters by average wait of customers who arrived near ``clock_minutes``.

    Returns ``(rows, used_all_day)``; rows are ``(counter, avg_wait, n_customers)``
    sorted quickest-first.  If nobody arrived within +/- ``window`` minutes the
    whole day is used and ``used_all_day`` is True.
    """
    needed = {"arrival_time", "counter", "wait_time"}
    if df is None or not needed.issubset(df.columns):
        return [], False
    served = df.dropna(subset=["wait_time"])
    if "balked" in served.columns:
        served = served[~served["balked"].astype(bool)]
    relative = clock_minutes - open_minutes
    near = served[(served["arrival_time"] - relative).abs() <= window]
    used_all_day = False
    if near.empty:
        near, used_all_day = served, True
    if near.empty:
        return [], used_all_day
    grouped = near.groupby("counter")["wait_time"].agg(["mean", "count"]).reset_index()
    grouped = grouped.sort_values("mean")
    return [(str(r["counter"]), float(r["mean"]), int(r["count"]))
            for _, r in grouped.iterrows()], used_all_day


# --------------------------------------------------------------------------- #
# Backend glue (calls teammates' code through the README contract)
# --------------------------------------------------------------------------- #
def _ensure_project_on_path() -> None:
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def import_backend(module: str, attr: str) -> Callable:
    """Import ``module.attr`` or raise ``BackendMissing`` with a friendly message."""
    _ensure_project_on_path()
    try:
        mod = importlib.import_module(module)
    except ModuleNotFoundError as exc:
        if exc.name and module.startswith(exc.name):
            raise BackendMissing(
                f"'{module}' was not found. It belongs to a teammate's part of the "
                f"project - pull the latest main and try again."
            ) from exc
        raise  # a real missing dependency (numpy etc.) - show it as an error
    try:
        return getattr(mod, attr)
    except AttributeError as exc:
        raise BackendMissing(f"'{module}' has no function called '{attr}'.") from exc


def normalise_customer_df(df: pd.DataFrame) -> pd.DataFrame:
    """Give a CSV-loaded customer table the dtypes the contract promises."""
    out = df.copy()
    for col in ("arrival_time", "service_start", "departure", "wait_time",
                "service_time", "order_value", "queue_length_on_arrival"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    if "balked" in out.columns and out["balked"].dtype != bool:
        out["balked"] = out["balked"].astype(str).str.strip().str.lower().isin(
            ["true", "1", "yes"])
    return out


def load_default_settings(config_path: Optional[str] = None) -> dict:
    """Form defaults from the real config file; falls back silently."""
    try:
        load_config = import_backend("config.config_loader", "load_config")
        return defaults_from_config(load_config(str(config_path or DEFAULT_CONFIG_PATH)))
    except Exception:
        return dict(DEFAULT_SETTINGS)


def run_pipeline(settings: dict, config_path: Optional[str] = None,
                 sample_csv: Optional[str] = None,
                 progress: Optional[Callable[[str], None]] = None) -> dict:
    """Run everything the UI needs and return it as one dict.

    Runs in a background thread, so it must never touch Tkinter.
    Result keys: config, df, metrics, hourly, scenarios, comparison,
    recommendation, scenario_error, source, settings.
    """
    say = progress or (lambda message: None)
    use_sample = sample_csv is not None

    compute_metrics = import_backend("analysis.metrics", "compute_metrics")
    hourly_wait_table = import_backend("analysis.metrics", "hourly_wait_table")

    say("Loading configuration...")
    try:
        load_config = import_backend("config.config_loader", "load_config")
        config = apply_settings_to_config(
            load_config(str(config_path or DEFAULT_CONFIG_PATH)), settings)
    except BackendMissing:
        if not use_sample:
            raise
        config = {}
    except FileNotFoundError:
        if not use_sample:
            raise
        config = {}

    result: dict[str, Any] = {
        "config": config, "df": None, "metrics": None, "hourly": None,
        "scenarios": None, "comparison": None, "recommendation": None,
        "scenario_error": None, "source": "sample" if use_sample else "simulation",
        "settings": settings,
    }

    if use_sample:
        say("Loading sample customers...")
        df = normalise_customer_df(pd.read_csv(sample_csv))
    else:
        run_simulation = import_backend("simulation.engine", "run_simulation")
        say("Running the simulation...")
        df = run_simulation(config, seed=settings.get("seed"))
    result["df"] = df

    say("Computing metrics...")
    result["metrics"] = compute_metrics(df, config)
    try:
        result["hourly"] = hourly_wait_table(df)
    except Exception:  # the Student view just shows a message without it
        result["hourly"] = None

    if use_sample:
        result["scenario_error"] = "Scenario comparison needs the real simulation (not sample data)."
        return result

    say("Comparing what-if scenarios...")
    try:
        run_all_scenarios = import_backend("simulation.scenarios", "run_all_scenarios")
        compare_scenarios = import_backend("analysis.report_generator", "compare_scenarios")
        generate_recommendation = import_backend("analysis.recommender", "generate_recommendation")
        scenarios = run_all_scenarios(config, seed=settings.get("seed"))
        comparison = compare_scenarios(scenarios)
        result["scenarios"] = scenarios
        result["comparison"] = comparison
        result["recommendation"] = generate_recommendation(comparison, config)
    except Exception as exc:  # keep the main results even if scenarios fail
        result["scenario_error"] = str(exc)
    return result
