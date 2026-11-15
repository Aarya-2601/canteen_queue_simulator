import pandas as pd

COLS = [
    "customer_id", "arrival_time", "counter", "items",
    "queue_length_on_arrival", "service_start", "departure",
    "wait_time", "service_time", "order_value", "balked"
]

def validate_simulation_data(df):
    if df is None or df.empty:
        raise ValueError("Dataframe is empty!")
    
    missing = [c for c in COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if (df["arrival_time"] < 0).any() or (df["order_value"] < 0).any():
        raise ValueError("Found negative arrival time or order value!")
    return True

def validate_config(config):
    if not isinstance(config, dict) or not config.get("counters"):
        raise ValueError("Invalid config: must be a dict with counters list.")
    return True