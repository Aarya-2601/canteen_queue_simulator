import pytest
import pandas as pd
from simulation.arrival_generator import ArrivalGenerator
from simulation.engine import run_simulation
from simulation.scenarios import run_all_scenarios
from simulation.calibration import calibrate_against_observed

@pytest.fixture
def test_cfg():
    return {
        "canteen_name": "VJTI Test",
        "simulation_minutes": 60,
        "counters": [
            {"name": "Snacks", "staff_count": 2, "efficiency_multiplier": 1.0, "balking_queue_limit": 5},
            {"name": "Beverages", "staff_count": 1, "efficiency_multiplier": 1.0, "balking_queue_limit": 5}
        ],
        "arrival_rates": {
            "test_slot": {"start": 0, "end": 60, "rate": 1.5}
        },
        "default_balking_limit": 5,
        "random_seed": 42
    }

def test_arrival_generator():
    gen = ArrivalGenerator(seed=42)
    n = gen.generate_arrivals(10)
    assert isinstance(n, int)
    assert n >= 0

def test_simulation_columns(test_cfg):
    df = run_simulation(test_cfg, seed=42)
    assert isinstance(df, pd.DataFrame)
    cols = ["customer_id", "arrival_time", "counter", "items", "queue_length_on_arrival", "service_start", "departure", "wait_time", "service_time", "order_value", "balked"]
    for c in cols:
        assert c in df.columns

def test_simulation_seed(test_cfg):
    df1 = run_simulation(test_cfg, seed=99)
    df2 = run_simulation(test_cfg, seed=99)
    pd.testing.assert_frame_equal(df1, df2)

def test_scenarios(test_cfg):
    res = run_all_scenarios(test_cfg, seed=42)
    assert "Current Setup" in res
    assert "Add One Counter" in res
    assert "Faster Billing" in res
    assert "Peak Hour Extra Staff" in res

def test_calibration():
    res = calibrate_against_observed("data/observed_arrivals.csv", seed=42)
    assert res["observed_total"] > 0
    assert res["simulated_total"] > 0
