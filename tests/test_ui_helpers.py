"""Tests for the pure-Python UI helpers (owner: Jiya).

These need no display and no Tkinter: run with  python -m pytest tests/test_ui_helpers.py
"""

import copy
import math

import numpy as np
import pandas as pd
import pytest

from ui import helpers as h


# ----------------------------------------------------------------- validation
def valid_raw(**overrides):
    raw = {"num_counters": "3", "staff_per_counter": "2", "peak_arrival_rate": "6.5",
           "balking_limit": "12", "seed": "42"}
    raw.update(overrides)
    return raw


def test_validate_accepts_good_input():
    clean, errors = h.validate_settings(valid_raw())
    assert errors == []
    assert clean == {"num_counters": 3, "staff_per_counter": 2, "peak_arrival_rate": 6.5,
                     "balking_limit": 12, "seed": 42}


def test_validate_blank_seed_means_random():
    clean, errors = h.validate_settings(valid_raw(seed="  "))
    assert errors == [] and clean["seed"] is None


@pytest.mark.parametrize("key,bad", [
    ("num_counters", ""),        # empty
    ("num_counters", "abc"),     # letters
    ("num_counters", "2.5"),     # not whole
    ("staff_per_counter", "-1"), # negative
    ("peak_arrival_rate", "0"),  # below minimum
    ("peak_arrival_rate", "nan"),
    ("peak_arrival_rate", "inf"),
    ("balking_limit", "1000"),   # too big
    ("seed", "-5"),
])
def test_validate_rejects_bad_input_without_raising(key, bad):
    clean, errors = h.validate_settings(valid_raw(**{key: bad}))
    assert len(errors) == 1
    assert key not in clean


def test_validate_reports_every_problem():
    _, errors = h.validate_settings(valid_raw(num_counters="x", balking_limit=""))
    assert len(errors) == 2


def test_validate_handles_missing_keys():
    _, errors = h.validate_settings({})
    assert len(errors) == 4  # everything required except the seed


# --------------------------------------------------------------------- config
BASE_CONFIG = {
    "counters": [{"name": "Snacks", "staff": 1}, {"name": "Thali", "staff": 2}],
    "peak_arrival_rate": 4.0, "balking_limit": 8,
}


def settings(**kw):
    base = {"num_counters": 2, "staff_per_counter": 3, "peak_arrival_rate": 7.0,
            "balking_limit": 10, "seed": 1}
    base.update(kw)
    return base


def test_apply_settings_does_not_mutate_original():
    original = copy.deepcopy(BASE_CONFIG)
    h.apply_settings_to_config(BASE_CONFIG, settings())
    assert BASE_CONFIG == original


def test_apply_settings_sets_values():
    cfg = h.apply_settings_to_config(BASE_CONFIG, settings())
    assert cfg["peak_arrival_rate"] == 7.0 and cfg["balking_limit"] == 10
    assert [c["staff"] for c in cfg["counters"]] == [3, 3]


def test_apply_settings_adds_and_removes_counters():
    more = h.apply_settings_to_config(BASE_CONFIG, settings(num_counters=4))
    assert [c["name"] for c in more["counters"]] == ["Snacks", "Thali", "Counter 3", "Counter 4"]
    fewer = h.apply_settings_to_config(BASE_CONFIG, settings(num_counters=1))
    assert [c["name"] for c in fewer["counters"]] == ["Snacks"]


def test_defaults_from_config():
    d = h.defaults_from_config(BASE_CONFIG)
    assert d["num_counters"] == 2 and d["peak_arrival_rate"] == 4.0 and d["balking_limit"] == 8
    assert h.defaults_from_config(None) == h.DEFAULT_SETTINGS


def test_get_open_hour():
    assert h.get_open_hour({"open_hour": 8}) == 8
    assert h.get_open_hour({}) == h.DEFAULT_OPEN_HOUR
    assert h.get_open_hour(None) == h.DEFAULT_OPEN_HOUR


# ----------------------------------------------------------------- formatting
def test_formatters_handle_missing_values():
    for fn in (h.fmt_minutes, h.fmt_percent, h.fmt_rupees, h.fmt_number):
        assert fn(None) == "—"
        assert fn(float("nan")) == "—"
    assert h.fmt_minutes(3.456) == "3.5 min"
    assert h.fmt_rupees(12345.6) == "₹12,346"


def test_clock_round_trip():
    assert h.minutes_to_clock(13 * 60 + 15) == "1:15 PM"
    assert h.minutes_to_clock(0) == "12:00 AM"
    assert h.minutes_to_clock(12 * 60) == "12:00 PM"
    assert h.parse_clock("1:15 PM") == 13 * 60 + 15
    assert h.parse_clock("12:00 AM") == 0
    assert h.parse_clock("13:15") == 13 * 60 + 15
    for text in ("", "banana", "25:00", "1:75 PM", "0:30 PM"):
        with pytest.raises(ValueError):
            h.parse_clock(text)


def test_time_choices_are_parseable():
    choices = h.time_choices()
    assert choices[0] == "11:00 AM" and "1:15 PM" in choices
    assert all(isinstance(h.parse_clock(c), int) for c in choices)


def test_kpi_items_and_empty_metrics():
    items = h.kpi_items({"avg_wait": 4.0, "p90_wait": 9.5, "balking_rate": 12.0,
                         "throughput_per_hour": 310.4, "total_revenue": 25000})
    assert [i["key"] for i in items] == ["avg_wait", "p90_wait", "balking_rate",
                                          "throughput_per_hour", "total_revenue"]
    assert items[0]["value"] == "4.0 min" and items[4]["value"] == "₹25,000"
    assert all(i["value"] == "—" for i in h.kpi_items(None))


def test_peak_queue_text():
    text = h.peak_queue_text({"peak_queue": 14, "peak_queue_time": 240}, open_hour=9)
    assert text == "Peak queue: 14 students at 1:00 PM"
    assert h.peak_queue_text({}) == ""


def test_counter_rows():
    rows = h.counter_rows({"utilisation": {"Snacks": 81.2}, "revenue_by_counter": {"Snacks": 5000, "Thali": 9000}})
    assert rows == [("Snacks", "81.2%", "₹5,000"), ("Thali", "—", "₹9,000")]
    assert h.counter_rows(None) == []


def test_dataframe_to_rows():
    df = pd.DataFrame({"scenario": ["Current", "Add Counter"], "avg_wait": [5.0, np.nan]})
    cols, rows = h.dataframe_to_rows(df)
    assert cols == ["scenario", "avg_wait"]
    assert rows == [["Current", "5.00"], ["Add Counter", "—"]]
    assert h.dataframe_to_rows(None) == ([], [])
    assert h.dataframe_to_rows(pd.DataFrame()) == ([], [])


# --------------------------------------------------------------- student view
def customers():
    return pd.DataFrame({
        "arrival_time": [240, 245, 250, 100, 255, 242],
        "counter": ["Snacks", "Snacks", "Thali", "Thali", "Thali", "Beverages"],
        "wait_time": [2.0, 4.0, 10.0, 1.0, 12.0, np.nan],
        "balked": [False, False, False, False, False, True],
    })


def test_quickest_counter_uses_window_and_ignores_balkers():
    rows, all_day = h.quickest_counter(customers(), clock_minutes=13 * 60, open_minutes=9 * 60)
    assert not all_day
    assert [r[0] for r in rows] == ["Snacks", "Thali"]  # Beverages only has a balker
    assert rows[0][1] == pytest.approx(3.0) and rows[0][2] == 2
    assert rows[1][1] == pytest.approx(11.0)             # the minute-100 customer is outside the window


def test_quickest_counter_falls_back_to_whole_day():
    rows, all_day = h.quickest_counter(customers(), clock_minutes=16 * 60, open_minutes=9 * 60)
    assert all_day and rows


def test_quickest_counter_bad_input():
    assert h.quickest_counter(None, 780, 540) == ([], False)
    assert h.quickest_counter(pd.DataFrame({"x": [1]}), 780, 540) == ([], False)


def test_best_time_finds_lowest_average():
    hourly = pd.DataFrame({"hour": [12, 13, 14], "avg_wait": [3.0, 9.0, 1.5], "p90_wait": [6, 15, 3]})
    assert h.best_time(hourly) == ("14", 1.5)
    assert h.best_time(None) is None
    assert h.best_time(pd.DataFrame()) is None
    nan_only = pd.DataFrame({"hour": [12], "avg_wait": [math.nan]})
    assert h.best_time(nan_only) is None


def test_best_time_with_unknown_column_names_uses_last_numeric():
    hourly = pd.DataFrame({"when": ["12-1", "1-2"], "wait": [5.0, 2.0]})
    assert h.best_time(hourly) == ("1-2", 2.0)


# --------------------------------------------------------------- backend glue
def test_import_backend_missing_module_is_friendly():
    with pytest.raises(h.BackendMissing):
        h.import_backend("no_such_teammate_module", "anything")


def test_import_backend_missing_function_is_friendly():
    with pytest.raises(h.BackendMissing):
        h.import_backend("json", "no_such_function")


def test_import_backend_works_for_real_function():
    assert h.import_backend("json", "dumps")({"a": 1}) == '{"a": 1}'


def test_normalise_customer_df_fixes_csv_types():
    raw = pd.DataFrame({"arrival_time": ["1", "2"], "wait_time": ["3.5", ""],
                        "balked": ["True", "False"]})
    out = h.normalise_customer_df(raw)
    assert out["balked"].tolist() == [True, False]
    assert out["arrival_time"].dtype.kind in "if"
    assert math.isnan(out["wait_time"].iloc[1])


def test_run_pipeline_with_sample_and_fake_backend(monkeypatch, tmp_path):
    """The glue calls the contract functions in order and returns the dict the UI expects."""
    csv = tmp_path / "sample.csv"
    customers().to_csv(csv, index=False)
    calls = []

    def fake_import(module, attr):
        calls.append((module, attr))
        if attr == "load_config":
            return lambda path: copy.deepcopy(BASE_CONFIG)
        if attr == "compute_metrics":
            return lambda df, cfg: {"avg_wait": 5.0}
        if attr == "hourly_wait_table":
            return lambda df: pd.DataFrame({"hour": [13], "avg_wait": [5.0]})
        raise AssertionError(f"unexpected backend call {module}.{attr}")

    monkeypatch.setattr(h, "import_backend", fake_import)
    messages = []
    result = h.run_pipeline(settings(), sample_csv=str(csv), progress=messages.append)

    assert result["source"] == "sample"
    assert result["metrics"] == {"avg_wait": 5.0}
    assert result["comparison"] is None and result["scenario_error"]
    assert result["config"]["balking_limit"] == 10
    assert messages  # progress was reported


def test_run_pipeline_full_run_with_fake_backend(monkeypatch):
    df = customers()
    fake = {
        "load_config": lambda path: copy.deepcopy(BASE_CONFIG),
        "run_simulation": lambda cfg, seed=None: df,
        "compute_metrics": lambda d, cfg: {"avg_wait": 1.0},
        "hourly_wait_table": lambda d: pd.DataFrame({"hour": [1], "avg_wait": [1.0]}),
        "run_all_scenarios": lambda cfg, seed=None: {"Current Setup": df},
        "compare_scenarios": lambda results: pd.DataFrame({"scenario": ["Current Setup"]}),
        "generate_recommendation": lambda comp, cfg: "Add a counter.",
    }
    monkeypatch.setattr(h, "import_backend", lambda module, attr: fake[attr])
    result = h.run_pipeline(settings())
    assert result["source"] == "simulation"
    assert result["recommendation"] == "Add a counter."
    assert result["scenario_error"] is None


def test_run_pipeline_scenario_failure_keeps_main_results(monkeypatch):
    df = customers()

    def boom(cfg, seed=None):
        raise RuntimeError("scenario crashed")

    fake = {
        "load_config": lambda path: copy.deepcopy(BASE_CONFIG),
        "run_simulation": lambda cfg, seed=None: df,
        "compute_metrics": lambda d, cfg: {"avg_wait": 1.0},
        "hourly_wait_table": lambda d: pd.DataFrame(),
        "run_all_scenarios": boom,
        "compare_scenarios": lambda r: None,
        "generate_recommendation": lambda c, cfg: "",
    }
    monkeypatch.setattr(h, "import_backend", lambda module, attr: fake[attr])
    result = h.run_pipeline(settings())
    assert result["metrics"] == {"avg_wait": 1.0}
    assert "scenario crashed" in result["scenario_error"]
