import os
import numpy as np
import pandas as pd
from simulation.arrival_generator import ArrivalGenerator

def calibrate_against_observed(obs_path="data/observed_arrivals.csv", cfg=None, seed=42):
    if not os.path.exists(obs_path):
        raise FileNotFoundError(f"File not found: {obs_path}")

    obs_df = pd.read_csv(obs_path)
    if "observed_arrivals" not in obs_df.columns:
        raise ValueError("Missing observed_arrivals column")

    rates = None
    if cfg is not None:
        rates = cfg.get("arrival_rates")

    gen = ArrivalGenerator(rates=rates, seed=seed)
    start_min = 210
    sim_counts = []

    for slot in range(len(obs_df)):
        slot_start = start_min + (slot * 5)
        slot_sum = 0
        for m in range(5):
            slot_sum += gen.generate_arrivals(slot_start + m)
        sim_counts.append(slot_sum)

    obs = obs_df["observed_arrivals"].to_numpy()
    sim = np.array(sim_counts)

    mae = float(np.mean(np.abs(sim - obs)))
    tot_obs = int(np.sum(obs))
    tot_sim = int(np.sum(sim))

    pct_err = 0.0
    if tot_obs > 0:
        pct_err = round(abs(tot_sim - tot_obs) / tot_obs * 100.0, 2)

    df_comp = obs_df.copy()
    df_comp["simulated"] = sim
    df_comp["diff"] = np.abs(sim - obs)

    status = "Needs calibration adjustments"
    if pct_err < 10.0:
        status = "Validated (Error < 10%)"

    return {
        "observed_total": tot_obs,
        "simulated_total": tot_sim,
        "mean_absolute_error_per_slot": round(mae, 2),
        "percentage_total_error": pct_err,
        "comparison_table": df_comp,
        "status": status
    }

if __name__ == "__main__":
    res = calibrate_against_observed()
    print(res["status"])
