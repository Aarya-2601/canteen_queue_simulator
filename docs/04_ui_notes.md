# UI Notes - Jiya

## App Structure
- Built with Tkinter + ttk; Matplotlib charts embedded using FigureCanvasTkAgg.
- `app.py` is the main window; `launch_app()` is called by `main.py`.
- Manager view has 5 tabs: Run Simulation, Results, Charts, Compare Scenarios, Reports.
- Student view shows the best time to visit and the quickest counter.
- All colours and fonts live in `styles.py`.

## Running a Simulation
- The simulation runs in a background thread so the window never freezes.
- The worker never touches widgets; it sends messages through a queue.
- The main thread reads the queue every 100 ms using `after()` and updates the progress bar.
- When finished, `on_result()` sends the results to every tab.

## Input Validation
- Every field is checked before the run starts.
- Checks: empty, letters, decimals in whole-number fields, negatives, out-of-range values.
- All problems are listed in one friendly messagebox, so the app never crashes.
- A blank seed means a random run; the same seed gives the same results.

## Results and Charts
- Results tab: KPI cards (average wait, 90th percentile wait, balking %, throughput, revenue) and a per-counter table.
- Charts tab: pick a chart, view it inside the app, and save it as PNG.
- Plot functions return a Matplotlib `Figure`, which `FigureCanvasTkAgg` displays.

## Scenarios and Student View
- Compare tab shows the scenario table, % improvement, recommendation text and chart.
- If scenarios fail, the other tabs still work.
- Quickest counter = lowest average wait of customers who arrived within 15 minutes of the chosen time.
- If nobody arrived near that time, the whole-day average is used.

## Testing
- `python -m pytest tests/test_ui_helpers.py` runs 41 tests with no display needed.
- Logic is kept in `helpers.py`, without Tkinter, so it can be tested.
- Manual check: app opens, bad input shows a popup, same seed gives same KPIs, every chart draws and saves.

## Integration
- Checked against the real config, simulation, analysis and chart code; a full run works end to end.
- Form settings map onto `canteen_config.json`: staff -> `staff_count`, balking limit -> `balking_queue_limit` / `default_balking_limit`, peak arrival rate -> scales all `arrival_rates` so the busiest slot equals the entered value.
- Key names live in `CONFIG_KEYS` at the top of `helpers.py`.
- Simulation minute 0 is 9:00 AM unless the config has `open_hour`.
- Utilisation arrives as a 0-1 fraction and is shown as a percentage.
- "Use sample data" loads `tests/dummy_customers.csv` for testing without the engine.