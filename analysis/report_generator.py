import os
import pandas as pd
from analysis.metrics import compute_metrics

def compare_scenarios(results):
    if not results:
        return pd.DataFrame()
    
    rows = []
    for name, df in results.items():
        m = compute_metrics(df)
        rows.append({
            "Scenario": name,
            "Avg Wait": m["avg_wait"],
            "P90 Wait": m["p90_wait"],
            "Balking %": m["balking_rate"],
            "Throughput": m["throughput_per_hour"],
            "Revenue": m["total_revenue"],
            "Lost Revenue": m["lost_revenue"]
        })
    comp = pd.DataFrame(rows).set_index("Scenario")
    base_wait = comp.iloc[0]["Avg Wait"] if not comp.empty else 0
    comp["% Wait Saved"] = ((base_wait - comp["Avg Wait"]) / base_wait * 100).round(1) if base_wait > 0 else 0
    return comp

def save_report(df, metrics, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("=== VJTI CANTEEN REPORT ===\n")
        for k, v in metrics.items():
            f.write(f"{k}: {v}\n")
    return path