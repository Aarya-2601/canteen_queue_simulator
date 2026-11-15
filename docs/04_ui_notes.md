# 04 - UI Notes (Jiya)

Desktop app for the VJTI Canteen Queue & Service Simulator, built with **Tkinter + ttk** and Matplotlib embedded through `FigureCanvasTkAgg`.

## 1. What I own

| File | Job |
| --- | --- |
| `ui/__init__.py` | Exposes `launch_app()` (imports the window lazily so helpers work without a display) |
| `ui/app.py` | Main window, Manager/Student switch, menu bar, About dialog, status bar, shared state |
| `ui/styles.py` | Colour palette, fonts, ttk theme (the only place with visual constants) |
| `ui/input_panel.py` | Settings form, validation, Run button, progress bar, background thread |
| `ui/results_panel.py` | KPI cards, per-counter table, and the Reports tab |
| `ui/charts_panel.py` | Chart picker, `FigureFrame` (embeds a `Figure`), Save chart |
| `ui/compare_panel.py` | Scenario table, recommendation text, comparison chart |
| `ui/student_view.py` | "Best time to visit" chart + "quickest counter" selector |
| `ui/helpers.py` | Pure-Python logic (no Tkinter): validation, formatting, Student-view maths, backend glue |
| `tests/test_ui_helpers.py` | 37 tests for `helpers.py` |

`helpers.py` is an extra file inside `ui/` (my folder). Keeping the logic away from the widgets is what makes it testable without a screen.

## 2. How the app is wired

```
main.py (Aarya) -> ui.launch_app() -> CanteenApp
                                       |- Manager view (Notebook)
                                       |    Run Simulation | Results | Charts | Compare Scenarios | Reports
                                       |- Student view
```

`CanteenApp.on_result(result)` is the single hub: when a run finishes it pushes the same `result` dict to every panel.

`result` keys: `config, df, metrics, hourly, scenarios, comparison, recommendation, scenario_error, source, settings`.

## 3. Calls into teammates' code (README section 7.2)

All of these go through `helpers.import_backend(module, function)`, so a missing module gives a friendly "pull the latest main" message instead of a crash.

| Call | Owner | Used in |
| --- | --- | --- |
| `load_config(path)` | Chaiti | `run_pipeline`, form defaults |
| `run_simulation(config, seed)` | Aarya | `run_pipeline` |
| `run_all_scenarios(config, seed)` | Aarya | `run_pipeline` |
| `compute_metrics(df, config)`, `hourly_wait_table(df)` | Janhavi | `run_pipeline` |
| `compare_scenarios(results)` | Janhavi | `run_pipeline` |
| `generate_recommendation(comparison, config)` | Janhavi | `run_pipeline` |
| `save_report(df, metrics, path)` | Janhavi | Reports tab |
| `plot_wait_by_hour, plot_queue_lengths, plot_utilisation, plot_wait_histogram, plot_scenario_comparison` | Chaiti | Charts, Compare, Student |
| `plot_dashboard` | Chaiti | Charts |

## 4. Design decisions

- **Background thread.** `run_pipeline` runs in a worker thread. The worker never touches a widget; it posts messages to a `queue.Queue` and the main thread polls it with `after(100, ...)`. Tkinter is not thread-safe, so this is the safe pattern, and the progress bar keeps moving.
- **Validation.** `validate_settings` returns `(clean, errors)` and never raises. Every problem is listed in one friendly messagebox (empty, letters, decimals in a whole-number field, negatives, out-of-range, NaN/inf). A blank seed means "random".
- **Errors never crash the app.** Worker errors are shown by `_show_error`; any unexpected Tk callback error goes through `report_callback_exception`.
- **Scenario failure is not fatal.** If the scenario step fails, the Results/Charts/Student views still work and the Compare tab explains why.
- **Sample data.** "Use sample data" loads `tests/dummy_customers.csv` so the UI can be built and demoed before the simulation engine is merged.
- **Charts.** Plot functions return a `Figure`; `FigureFrame` embeds it and closes the old one so memory does not grow.
- **Student view.** "Quickest counter" averages `wait_time` of served customers who arrived within +/- 15 minutes of the chosen time. If nobody did, it uses the whole day and says so.

## 5. Assumptions to confirm with teammates

I could not see the other folders' code while writing this, so these are guesses, all isolated at the top of `ui/helpers.py`:

1. **Config key names** (`CONFIG_KEYS`): `counters` (list of dicts with `name` and `staff`), `peak_arrival_rate`, `balking_limit`. Ask Chaiti; if different, edit only that dict.
2. **Opening hour** (`OPEN_HOUR_KEYS`, default 9): minute 0 of the simulation is 9:00 AM unless the config says otherwise. Used for the clock time in the Student view.
3. **Module paths**: `simulation.engine.run_simulation`, `simulation.scenarios.run_all_scenarios`, `analysis.metrics`, `analysis.report_generator` (`compare_scenarios`, `save_report`), `analysis.recommender`, `visualization.plots`, `visualization.dashboard`.
4. **Hourly table columns**: I look for `hour`/`avg_wait` style names and fall back to the first/last numeric column.
5. **Comparison table**: displayed with whatever columns Janhavi returns.

## 6. Testing

- Automatic: `python -m pytest tests/test_ui_helpers.py` (no display needed).
- Manual checklist (needs a screen):
  1. `python main.py` opens with no error.
  2. Run with defaults: progress bar moves, window stays responsive, Results tab opens.
  3. Type letters / leave empty / enter -3: a messagebox lists the problems, no crash.
  4. Same seed twice gives identical KPI numbers.
  5. Every entry in the Charts picker draws; "Save chart" writes a PNG.
  6. Compare tab shows the table, % improvement and recommendation.
  7. Student view: pick 1:15 PM, a quickest counter appears.
  8. Reports tab saves TXT and CSV.

## 7. Viva answers (UI)

- **Why a background thread?** The Tkinter event loop runs on the main thread. A long simulation there would block it and the window would freeze. The worker does the heavy work and hands results back through a queue.
- **Why a queue and `after()`?** Widgets may only be changed from the main thread; `after()` polls the queue from inside the event loop.
- **How is bad input handled?** All values are validated before the run; errors go in a messagebox and nothing is started.
- **How do charts get into Tkinter?** Chaiti's functions return `Figure` objects; `FigureCanvasTkAgg` renders a `Figure` inside a Tk frame.
- **Why keep `helpers.py` free of Tkinter?** So the logic can be unit-tested and reused without a display.
