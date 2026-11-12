# 🍽️ VJTI Canteen Queue & Service Simulator

A Python simulation and decision-support tool for the **VJTI college canteen**. It models how students queue and get served during the day, then answers the questions a canteen manager actually asks:

- *"How long do students wait at lunch rush?"*
- *"If we add one more counter or one more staff member, how much does the wait drop?"*
- *"When is the best time for a student to visit?"*

- **Course:** Python Mini Project, Second Year B.Tech IT, VJTI
- **Team Members:**
  - **Aarya** (Simulation Engine, Scenarios, Integration)
  - **Chaiti** (Models, Config, Charts, Field Data)
  - **Janhavi** (Data Handling, Analysis, Recommendations)
  - **Jiya** (Desktop App & User Experience)

---

## 1. The Problem

Between roughly **1:00 PM and 2:00 PM**, the VJTI canteen gets crowded. Students lose break time standing in queues, some give up and leave without ordering (**balking**), and the load is uneven across counters. Right now there is no data-driven way to decide staffing or counter changes.

### Our Solution
A minute-by-minute simulation of the canteen, calibrated with real arrival data collected at VJTI, with a clean desktop app on top so that canteen staff and students can use it without touching code.

---

## 2. What We Are Building

| Layer | What it does |
| :--- | :--- |
| **Simulation engine** | Generates random customer arrivals using a **Negative Binomial distribution** (to capture bursty, group-based arrivals when classes let out), places them in counter queues, serves them, and records every event. |
| **Models and config** | `Customer`, `Counter`, and `MenuItem` classes. Counters, staff, rates, and menu are loaded from editable files. |
| **Analysis** | Average, median, max, and 90th percentile wait, peak queue, utilisation, balking rate, throughput, revenue, scenario comparison, and an auto-written recommendation. |
| **Visualisation** | Matplotlib charts that are also embedded inside the app. |
| **Desktop app (GUI)** | Tkinter interface with a Manager view and a Student view. |

### Simulation Approach (Kept Simple on Purpose)
A minute-by-minute discrete time-step loop. In each simulated minute:
1. **New customers arrive:** Using `numpy.random.negative_binomial`. The arrival rate $\lambda(t)$ depends on the time of day, and the Negative Binomial distribution accurately captures overdispersion and clumping when lectures dismiss.
2. **Queue selection & balking:** Each customer evaluates queue length and joins a counter queue, or leaves if the line is too long (balking).
3. **Service start:** Free counter staff pick the next waiting customer.
4. **Service countdown:** Busy counters count down remaining service time.
5. **Departure:** Finished customers leave and are logged.

> **Design note:** No SimPy or heavy frameworks. Only loops, conditionals, lists, dicts, and classes, plus NumPy, Pandas, and Matplotlib.

---

## 3. Why Negative Binomial Instead of Poisson?

Standard queueing simulations frequently assume a Poisson process for arrivals. However, in an engineering college canteen like VJTI:
- **Independent arrival assumption fails:** Students do not arrive individually at random intervals. Instead, they arrive in **bursty, clumped groups** right after lecture and lab bells ring (particularly around 12:30 PM to 2:00 PM).
- **Overdispersion ($\sigma^2 > \mu$):** Real canteen footfall displays higher variance than mean. A Poisson distribution forces variance to equal mean ($\sigma^2 = \mu$), underestimating the sudden shock of peak lunch rush queues.
- **Negative Binomial formulation:** Parameterized by target arrival rate $\lambda(t)$ and dispersion parameter $r$:
  $$p = \frac{r}{r + \lambda(t)}, \quad \text{Mean} = \frac{r(1-p)}{p} = \lambda(t), \quad \text{Variance} = \lambda(t) \left(1 + \frac{\lambda(t)}{r}\right) > \lambda(t)$$
  This reliably reproduces realistic queue spikes and sudden congestion waves.

---

## 4. The App (UI Plan)

Built with **Tkinter + ttk** (ships with Python) and Matplotlib embedded via `FigureCanvasTkAgg`.

### Manager View (Tabs)

| Tab | Content |
| :--- | :--- |
| **Run Simulation** | Form to set counters, staff per counter, peak arrival rate, balking limit, and random seed. A "Run" button with a progress bar. |
| **Results** | KPI cards (Avg Wait, 90th Percentile Wait, Balking %, Throughput, Revenue) plus a table per counter. |
| **Charts** | Wait by hour, queue length over time, utilisation, wait histogram, and the 2×2 dashboard. |
| **Compare Scenarios** | Current setup vs. Add Counter vs. Faster Billing vs. Extra Peak Staff, with % improvement and recommendation text. |
| **Reports** | Save or open the generated report (TXT/CSV) and chart images. |

### Student View
- A **"Best time to visit"** chart showing expected wait by hour.
- A selector: *"I want to eat at 1:15 PM, which counter is quickest?"*

### UI Rules
- The simulation runs in a background thread so the window never freezes (progress bar shown).
- Every input is validated, with friendly messagebox errors instead of crashes.
- Consistent colours and fonts defined in one place (`ui/styles.py`).
- Charts are returned as Matplotlib `Figure` objects so the UI can embed them (the contract between Chaiti and Jiya).

---

## 5. Folder Structure and Ownership

> **Golden Rule:** Every folder or file has exactly **one owner**. Never edit a file you don't own. This is how we get zero merge conflicts.

```text
vjti-canteen-simulation/
├── main.py                        # Aarya: launches the app
├── README.md                      # Aarya
├── requirements.txt               # Aarya
├── .gitignore                     # Aarya
│
├── simulation/                    # Aarya (whole folder)
│   ├── __init__.py
│   ├── engine.py
│   ├── arrival_generator.py
│   ├── scenarios.py
│   └── calibration.py
│
├── models/                        # Chaiti (whole folder)
│   ├── __init__.py
│   ├── customer.py
│   ├── counter.py
│   └── menu_item.py
│
├── config/                        # Chaiti (whole folder)
│   ├── canteen_config.json
│   └── config_loader.py
│
├── visualization/                 # Chaiti (whole folder)
│   ├── __init__.py
│   ├── plots.py
│   └── dashboard.py
│
├── data/
│   ├── menu.csv                   # Chaiti
│   ├── observed_arrivals.csv      # Chaiti (collected by the whole team)
│   └── logs/                      # auto-generated, gitignored
│
├── data_handler/                  # Janhavi (whole folder)
│   ├── __init__.py
│   ├── file_manager.py
│   ├── logger.py
│   └── validator.py
│
├── analysis/                      # Janhavi (whole folder)
│   ├── __init__.py
│   ├── metrics.py
│   ├── report_generator.py
│   └── recommender.py
│
├── ui/                            # Jiya (whole folder)
│   ├── __init__.py
│   ├── app.py                     # main window and navigation
│   ├── styles.py                  # colours, fonts, ttk theme
│   ├── input_panel.py             # settings form and validation
│   ├── results_panel.py           # KPI cards and tables
│   ├── charts_panel.py            # embeds Matplotlib figures
│   ├── compare_panel.py           # scenario comparison tab
│   └── student_view.py            # "best time to visit" view
│
├── outputs/                       # auto-generated, gitignored
│   ├── charts/
│   └── reports/
│
├── tests/
│   ├── dummy_customers.csv        # Janhavi (created once on Day 1 for parallel dev)
│   ├── test_simulation.py         # Aarya
│   ├── test_models_config.py      # Chaiti
│   ├── test_analysis.py           # Janhavi
│   └── test_ui_helpers.py         # Jiya
│
└── docs/
    ├── 01_simulation_notes.md         # Aarya
    ├── 02_models_visualization_notes.md  # Chaiti
    ├── 03_data_analysis_notes.md      # Janhavi
    └── 04_ui_notes.md                 # Jiya
```

---

## 6. Work Distribution

### 👩‍💻 Aarya: Simulation Engine, Scenarios and Integration
- **`engine.py`**: `CanteenSimulation` class with the minute-by-minute time-step loop (Negative Binomial arrivals, queue joining, service countdown, departure, balking).
- **`arrival_generator.py`**: Negative Binomial arrivals with time-of-day rates ($\lambda$) and dispersion parameter ($r$), with reproducible seed support.
- **`scenarios.py`**: *"Current Setup"*, *"Add One Counter"*, *"Faster Billing"*, *"Peak Hour Extra Staff"*, plus `run_all_scenarios()`.
- **`calibration.py`**: Compares simulated Negative Binomial arrivals with `observed_arrivals.csv` and computes error metrics.
- **`main.py`**, **`README.md`**, **`requirements.txt`**, **`.gitignore`**, **`tests/test_simulation.py`**, and **`docs/01_simulation_notes.md`**.

### 👩‍💻 Chaiti: Models, Config, Charts and Field Data
- **`customer.py`**, **`counter.py`**, **`menu_item.py`**: Classes with `__init__`, `__str__`, `__repr__`, and methods like `wait_time()`, `add_to_queue()`, `is_free()`, `utilisation()`.
- **`canteen_config.json`** and **`config_loader.py`**: Configuration loading and validation.
- **`menu.csv`** (15 to 20 real VJTI canteen items) and menu parser.
- **`observed_arrivals.csv`**: Data entry and cleaning after field visit.
- **`plots.py`**: Wait by hour, queue length over time, utilisation, wait histogram, scenario comparison bars (each returns a `Figure`).
- **`dashboard.py`**: 2×2 combined dashboard figure.
- **`tests/test_models_config.py`** and **`docs/02_models_visualization_notes.md`**.

### 👩‍💻 Janhavi: Data Handling, Analysis and Recommendations
- **`file_manager.py`**: Save/load logs as CSV, folder management, error handling (`FileNotFoundError`, `PermissionError`).
- **`logger.py`**: Timestamped simulation event logs (`[13:05] Customer #42 joined Snacks queue (length 6)`).
- **`validator.py`**: Validation checks for config and UI input data (negatives, missing columns, types).
- **`metrics.py`**: Average, median, max, and 90th percentile wait, peak queue and time, utilisation, balking rate, throughput, revenue per counter, and `hourly_wait_table()`.
- **`report_generator.py`**: Text and CSV report export, scenario comparison table with % improvement.
- **`recommender.py`**: Plain-English recommendation with cost-benefit analysis (staff cost vs. revenue saved from fewer balked customers).
- **`tests/dummy_customers.csv`**, **`tests/test_analysis.py`**, and **`docs/03_data_analysis_notes.md`**.

### 👩‍💻 Jiya: Desktop App and User Experience
- **`app.py`**: Main Tkinter window, tabs, Manager/Student view switch, menu bar, and About dialog.
- **`styles.py`**: Colour palette, fonts, and ttk theme tokens.
- **`input_panel.py`**: Settings form (spinboxes, entries), input validation, Run button, progress bar, background thread.
- **`results_panel.py`**: KPI cards and per-counter `ttk.Treeview` table.
- **`charts_panel.py`**: Embeds Matplotlib figures via `FigureCanvasTkAgg`, chart picker, "Save chart" button.
- **`compare_panel.py`**: Scenario comparison table and recommendation display.
- **`student_view.py`**: "Best time to visit" chart and quickest counter selector.
- **`tests/test_ui_helpers.py`** and **`docs/04_ui_notes.md`**.

---

## 7. The Shared Interface Contract

The contract defines the integration bridge. It allows all four team members to build and test their modules independently in parallel using mock fixtures.

### 7.1 Customer DataFrame Columns (Output of the Simulation)

| Column | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | `int` | Unique integer identifier |
| `arrival_time` | `int` | Minute of arrival since canteen opening |
| `counter` | `str` | Counter name, e.g. `"Snacks"`, `"Thali"`, `"Beverages"` |
| `items` | `str` | Semicolon-separated list of items ordered |
| `queue_length_on_arrival` | `int` | Number of people already in that queue |
| `service_start` | `float` / `int` | Minute service began (`np.nan` if balked) |
| `departure` | `float` / `int` | Minute customer departed (`np.nan` if balked) |
| `wait_time` | `float` / `int` | `service_start - arrival_time` (`np.nan` if balked) |
| `service_time` | `float` / `int` | `departure - service_start` (`0` if balked) |
| `order_value` | `float` | Total price in ₹ |
| `balked` | `bool` | `True` if customer left without ordering |

*All times are integer minutes since opening.*

### 7.2 Standard Function Signatures

| Owner | Function Signature | Return Type | Description |
| :--- | :--- | :--- | :--- |
| **Chaiti** | `load_config(path: str) -> dict` | `dict` | Loads and validates canteen config JSON |
| **Chaiti** | `load_menu(path: str) -> list[MenuItem]` | `list` | Parses menu CSV into `MenuItem` objects |
| **Aarya** | `run_simulation(config: dict, seed: int = None) -> pd.DataFrame` | `pd.DataFrame` | Executes full minute-by-minute simulation run |
| **Aarya** | `run_all_scenarios(base_config: dict, seed: int = None) -> dict[str, pd.DataFrame]` | `dict` | Executes all predefined "what-if" scenarios |
| **Janhavi** | `compute_metrics(df: pd.DataFrame, config: dict) -> dict` | `dict` | Computes comprehensive KPI metric dictionary |
| **Janhavi** | `hourly_wait_table(df: pd.DataFrame) -> pd.DataFrame` | `pd.DataFrame` | Aggregates hourly average and P90 wait times |
| **Janhavi** | `compare_scenarios(results: dict[str, pd.DataFrame]) -> pd.DataFrame` | `pd.DataFrame` | Summary comparison table across scenarios |
| **Janhavi** | `generate_recommendation(comparison_df: pd.DataFrame, config: dict) -> str` | `str` | Plain-English cost-benefit recommendation |
| **Janhavi** | `save_report(df: pd.DataFrame, metrics: dict, path: str) -> str` | `str` | Exports summary report to disk |
| **Chaiti** | `plot_wait_by_hour(df: pd.DataFrame) -> matplotlib.figure.Figure` | `Figure` | Hourly wait time bar/line chart |
| **Chaiti** | `plot_queue_lengths(df: pd.DataFrame) -> matplotlib.figure.Figure` | `Figure` | Queue length timeline chart |
| **Chaiti** | `plot_utilisation(df: pd.DataFrame) -> matplotlib.figure.Figure` | `Figure` | Counter utilisation rate bar chart |
| **Chaiti** | `plot_wait_histogram(df: pd.DataFrame) -> matplotlib.figure.Figure` | `Figure` | Wait time frequency distribution |
| **Chaiti** | `plot_scenario_comparison(comparison_df: pd.DataFrame) -> matplotlib.figure.Figure` | `Figure` | Scenario KPI comparison chart |
| **Chaiti** | `plot_dashboard(df: pd.DataFrame) -> matplotlib.figure.Figure` | `Figure` | 2×2 composite performance dashboard |
| **Jiya** | `launch_app() -> None` | `None` | Instantiates and launches the Tkinter desktop GUI |

### 7.3 Metrics Dictionary Keys

The dictionary returned by `compute_metrics(df, config)` contains:
- `avg_wait`: Overall average waiting time in minutes.
- `median_wait`: Median waiting time in minutes.
- `max_wait`: Maximum recorded waiting time.
- `p90_wait`: 90th percentile wait time (critical service KPI).
- `peak_queue`: Maximum observed queue length across all counters.
- `peak_queue_time`: Simulation minute when peak queue occurred.
- `balking_rate`: Percentage of arrived customers who walked away due to long queues.
- `throughput_per_hour`: Total served customers divided by simulation operating hours.
- `total_revenue`: Total ₹ earned by the canteen from completed orders.
- `utilisation`: Dict of `{counter_name: utilisation_percentage}`.
- `revenue_by_counter`: Dict of `{counter_name: total_counter_revenue}`.

---

## 8. Git Workflow

- `main` is protected. Nobody pushes directly without review.
- Branches:
  - `feature/aarya-simulation`
  - `feature/chaiti-models-viz`
  - `feature/janhavi-analysis`
  - `feature/jiya-ui`
- Run `git pull origin main` every day before starting work.
- Commit small and often, with clear messages:
  - ✅ `feat(simulation): add negative binomial arrival rates`
  - ❌ `update`, `final`, `changes`
- When a module is done, open a Pull Request and have one teammate review it before merging.
- Only touch files you own (see Section 5).

---

## 9. Canteen Field Data Collection

The team conducts a lunch rush visit to calibrate arrival rates and service durations:
- **Aarya:** Arrivals at the entrance, counted per 5-minute slot.
- **Chaiti:** Queue length at each counter, recorded every 5 minutes.
- **Janhavi:** Service time for 15 to 20 customers using a stopwatch.
- **Jiya:** Menu items, prices, number of staff per counter, and photos for the presentation.

Data is stored in [`data/observed_arrivals.csv`](file:///data/observed_arrivals.csv) and [`data/menu.csv`](file:///data/menu.csv).

---

## 10. How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the app
python main.py

# 3. Run tests
python -m pytest tests/
```

---

## 11. Definition of "Done"

- [x] `python main.py` opens the app with no errors.
- [x] A simulation runs from the UI in under 10 seconds with a visible progress bar.
- [x] Results and all charts display inside the app.
- [x] Scenario comparison shows % improvement and a written recommendation.
- [x] Student view shows the best time to visit.
- [x] Bad input (empty fields, negatives, letters) shows a friendly message and never crashes the app.
- [x] Same seed gives the same results every time.
- [x] Every function has a docstring and every module has tests or notes.
- [x] Each member has meaningful commits and can explain the entire pipeline.

---

## 12. Viva Questions We Should Be Ready For

1. **Why Negative Binomial distribution instead of Poisson for arrivals?**
   Poisson assumes independent arrivals with equal mean and variance ($\sigma^2 = \mu$). In a college canteen, arrivals are clumped into groups when lectures let out, resulting in **overdispersion** ($\sigma^2 > \mu$). Negative Binomial models this group burstiness accurately.
2. **How did you check that the simulation matches the real canteen?**
   `calibration.py` compares simulated Negative Binomial arrivals against empirical field data in `observed_arrivals.csv` across 5-minute lunch slots.
3. **Why is the 90th percentile wait more useful than the average?**
   Averages hide tail latency. An average wait of 5 minutes might sound fine, but a P90 of 15 minutes means 10% of students lose a third of their lunch break waiting in line.
4. **What is balking and why did you model it?**
   Balking is when an arriving customer sees an excessively long queue and decides to walk away without ordering. Modeling it is critical to capturing lost canteen revenue.
5. **Why does the simulation run in a background thread in the UI?**
   Running the simulation on the main Tkinter thread would block the GUI event loop and freeze the window. Threading ensures the progress bar and UI stay responsive.
6. **Explain how a customer moves through the system, from arrival to departure.**
   Arrival $\to$ Counter Queue Selection $\to$ Balking Check $\to$ Wait in Queue $\to$ Service at Staff Counter $\to$ Departure & Logging.

---

## 13. Stretch Goals

- [ ] Token / pre-order scenario that cuts wait times.
- [ ] Export the final report as PDF.
- [ ] Light and dark theme toggle.
- [ ] Command-line mode using `argparse`.
- [ ] Heatmap of hour × counter congestion.
