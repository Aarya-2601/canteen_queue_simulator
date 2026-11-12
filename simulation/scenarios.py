import copy
import pandas as pd
from simulation.engine import run_simulation

def get_scenario_configs(base_cfg):
    scenarios = {}
    scenarios["Current Setup"] = copy.deepcopy(base_cfg)

    sc_add = copy.deepcopy(base_cfg)
    sc_add["counters"].append({
        "name": "Express Counter",
        "staff_count": 1,
        "efficiency_multiplier": 1.2,
        "balking_queue_limit": 10
    })
    scenarios["Add One Counter"] = sc_add

    sc_fast = copy.deepcopy(base_cfg)
    for c in sc_fast["counters"]:
        eff = c.get("efficiency_multiplier", 1.0)
        c["efficiency_multiplier"] = round(eff * 1.35, 2)
    scenarios["Faster Billing"] = sc_fast

    sc_staff = copy.deepcopy(base_cfg)
    for c in sc_staff["counters"]:
        name = c["name"].lower()
        if "snack" in name or "thali" in name:
            c["staff_count"] = c.get("staff_count", 1) + 1
    scenarios["Peak Hour Extra Staff"] = sc_staff

    return scenarios

def run_all_scenarios(base_cfg, seed=None, progress_callback=None):
    configs = get_scenario_configs(base_cfg)
    results = {}
    total = len(configs)
    index = 0
    for name, cfg in configs.items():
        if progress_callback:
            pct = int((index / total) * 100)
            progress_callback(pct, name)
        results[name] = run_simulation(cfg, seed=seed)
        index += 1
    if progress_callback:
        progress_callback(100, "Done")
    return results
