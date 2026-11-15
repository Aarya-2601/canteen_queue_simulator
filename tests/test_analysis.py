import pandas as pd
from analysis.metrics import compute_metrics
from data_handler.validator import validate_simulation_data

def test_metrics():
    df = pd.read_csv("tests/dummy_customers.csv")
    validate_simulation_data(df)
    m = compute_metrics(df)
    assert m["avg_wait"] >= 0
    assert 0 <= m["balking_rate"] <= 100
    assert "lost_revenue" in m