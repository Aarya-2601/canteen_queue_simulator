import argparse
import tkinter as tk
from config.config_loader import load_config
from simulation.engine import run_simulation
from analysis.metrics import compute_metrics
from analysis.report_generator import save_report
from ui.app import launch_app

def run_cli(cfg_path="config/canteen_config.json"):
    print("VJTI Canteen Queue Simulator (CLI)")
    cfg = load_config(cfg_path)
    seed = cfg.get("random_seed", 42)
    df = run_simulation(cfg, seed=seed)
    m = compute_metrics(df, cfg)
    print("Avg Wait:", m.get("avg_wait"))
    print("P90 Wait:", m.get("p90_wait"))
    print("Balking %:", m.get("balking_rate"))
    print("Throughput:", m.get("throughput_per_hour"))
    print("Revenue:", m.get("total_revenue"))
    save_report(df, m, "outputs/reports/cli_report.txt")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cli", action="store_true")
    p.add_argument("--config", default="config/canteen_config.json")
    args = p.parse_args()

    if args.cli:
        run_cli(args.config)
    else:
        try:
            launch_app()
        except tk.TclError:
            run_cli(args.config)

if __name__ == "__main__":
    main()
