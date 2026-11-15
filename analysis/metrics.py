import numpy as np
import pandas as pd

def compute_metrics(df, config=None):
    served = df[~df["balked"]]
    balked = df[df["balked"]]

    waits = served["wait_time"].dropna()
    max_dep = df["departure"].max() if not df.empty and not df["departure"].empty else 1
    total_time = max(max_dep, 1) if pd.notna(max_dep) else 1

    # utilisation per counter: busy time / total sim time
    busy = served.groupby("counter")["service_time"].sum()
    utilisation = {c: round(min(t / total_time, 1.0), 3) for c, t in busy.items()}

    return {
        "avg_wait": round(waits.mean(), 2) if not waits.empty else 0.0,
        "median_wait": round(waits.median(), 2) if not waits.empty else 0.0,
        "max_wait": round(waits.max(), 2) if not waits.empty else 0.0,
        "p90_wait": round(np.percentile(waits, 90), 2) if not waits.empty else 0.0,
        "peak_queue": int(df["queue_length_on_arrival"].max()) if not df.empty else 0,
        "peak_queue_time": int(df.loc[df["queue_length_on_arrival"].idxmax(), "arrival_time"]) if not df.empty else 0,
        "balking_rate": round(len(balked) / len(df) * 100, 2) if len(df) > 0 else 0.0,
        "throughput_per_hour": round(len(served) / (total_time / 60), 2),
        "total_revenue": round(served["order_value"].sum(), 2),
        "lost_revenue": round(balked["order_value"].sum(), 2),
        "utilisation": utilisation,
        "revenue_by_counter": served.groupby("counter")["order_value"].sum().to_dict()
    }

def hourly_wait_table(df):
    served = df[~df["balked"]].copy()
    served["hour"] = served["arrival_time"] // 60
    return served.groupby("hour")["wait_time"].mean().round(1).reset_index()