# 🍽️ VJTI Canteen Queue & Service Simulator

A Python-based discrete-time simulation and decision-support tool tailored for the **VJTI college canteen**. It models student arrival dynamics, queue formation, counter operations, and service bottlenecks during peak college hours, providing actionable insights for both canteen management and students.

- **Course:** Python Mini Project, Second Year B.Tech IT, VJTI
- **Team Members:**
  - **Aarya** (Simulation Engine, Scenarios, Integration)
  - **Chaiti** (Models, Config, Charts, Field Data)
  - **Janhavi** (Data Handling, Analysis, Recommendations)
  - **Jiya** (Desktop App & User Experience)

---

## 1. The Problem

Between **1:00 PM and 2:00 PM** (the primary college lunch break), the VJTI canteen experiences severe congestion:
- Students lose a large portion of their break standing in unmanaged queues.
- Some students give up and leave without ordering (**balking**), causing lost canteen revenue.
- Service load is highly uneven across counters (e.g., Snacks vs. Thali vs. Beverages).
- Decisions regarding counter staffing or opening additional billing counters are currently made through guesswork rather than data.

### Our Solution
A minute-by-minute discrete-event simulation calibrated with real observation data collected at the VJTI canteen. The engine is bundled with an interactive Tkinter desktop GUI featuring:
- **Manager View:** Adjust staffing, analyze KPIs, visualize queues, compare "what-if" operational scenarios, and generate management reports.
- **Student View:** Determine the best time to visit and identify the fastest counter for their lunch slot.

---

## 2. System Architecture & Simulation Engine

The simulation intentionally avoids heavyweight external simulation frameworks (e.g., SimPy) to focus on transparent, modular Python principles: object-oriented programming, standard loops, conditionals, NumPy, Pandas, and Matplotlib.

### Simulation Mechanics (Minute-by-Minute Time-Step Loop)
For each simulated minute ($t = 0, 1, 2, \dots, T$):
1. **Arrival Generation:** Generates new customer arrivals. Rate $\lambda(t)$ varies dynamically based on time of day (morning lull, lunch rush peak, afternoon quiet).
2. **Queue Selection & Balking:** Arriving customers evaluate counter queue lengths. If the queue length exceeds their patience threshold (balking limit), they leave without ordering.
3. **Queue Assignment:** Non-balking customers join the shortest or designated counter queue.
4. **Service Allocation:** Idle counter staff pick the next customer from the queue. Service time is determined based on the ordered menu items and counter efficiency.
5. **Service Countdown:** Active counters decrement remaining service time.
6. **Dining & Table Allocation:** After receiving their order, customers transition to a dining state if tables are tracked, occupying seats until dining is complete.
7. **Departure & Logging:** Completed customers are timestamped, logged, and exited from the system.

---

## 3. Simulation Engine Enhancements

Based on operational analysis and domain review of college canteens, four major architectural enhancements have been integrated into the system design:

### 3.1 Simulation Engine & Arrival Distributions (Negative Binomial Transition)
- **The Limitation of Poisson:** A standard Poisson process assumes independent, memoryless arrivals where variance equals the mean ($\sigma^2 = \mu$). However, in a college environment, students arrive in **bursty, clumped groups** immediately after lecture bells ring (notably between **12:30 PM and 2:30 PM**).
- **The Negative Binomial Solution:** Transitioning to or supporting a **Negative Binomial distribution** ($r, p$) during peak rush captures this **overdispersion** ($\sigma^2 > \mu$). This accurately simulates batch/group arrivals when entire lecture batches dismiss simultaneously.

### 3.2 Item Popularity & Combo Bundling
- **Popularity-Weighted Selection:** Instead of uniform random item selection, customer order sampling uses an empirical **popularity-weighted probability distribution** derived from sales frequencies in [`data/menu.csv`](file:///data/menu.csv).
- **Inventory & Stock Tracking:** Simulates depletion of fast-moving items (e.g., Samosa Pav, Misal Pav) over the course of the day.
- **Pre-Assembled Combo Bundling:** Frequently co-ordered items (e.g., *"Samosa Pav + Cutting Chai"*) can be ordered as pre-packaged combos, cutting kitchen preparation and transaction durations by 25–40%.

### 3.3 Seating and Table Allocation
- **Tables as a Constrained Resource:** Incorporates a dining hall table capacity model (`Table` / `DiningHall`) alongside counter queues.
- **Full Customer Lifecycle:** Customers transition across explicit states:  
  $$\text{Arrival} \longrightarrow \text{Counter Queue} \longrightarrow \text{Service / Billing} \longrightarrow \text{Dining Table} \longrightarrow \text{Departure}$$
- **Total Dwell Time:** Measures total customer time in the canteen:  
  $$\text{Dwell Time} = \text{Queue Wait Time} + \text{Service Duration} + \text{Dining Duration}$$
  Identifies whether the canteen's primary bottleneck is **counter service capacity** or **dining seating capacity**.

### 3.4 Scenario Comparison & Experimentation
Leveraging [`simulation/scenarios.py`](file:///simulation/scenarios.py) to test multi-variable operational policies and quantify percentage improvements:
1. **Baseline ("Current Setup"):** Default counters, staffing, and seating.
2. **Add One Counter:** Additional express billing / quick-serve counter.
3. **Faster Billing / POS:** Barcode/UPI token screen acceleration (+35% speedup).
4. **Peak Hour Extra Staff:** Flex staffing during the 12:30–2:30 PM window.
5. **Seating Capacity Expansion:** Evaluating table turnover when seating is increased.
6. **Combo Pre-Assembly:** Speedup benefits from high-demand pre-packed combos.

---

## 4. The Desktop Application (UI Plan)

Built with **Tkinter + ttk** and Matplotlib figures embedded using `FigureCanvasTkAgg`.

### Manager View
- **Run Simulation:** Interactive input form (counters, staff per counter, peak arrival rate, balking limit, arrival distribution mode, table capacity, random seed) with a responsive progress bar powered by a background worker thread.
- **Results:** Clean KPI summary cards (Avg Wait, P90 Wait, Balking %, Throughput, Total Revenue, Table Occupancy %, Avg Dwell Time) and a per-counter performance breakdown table (`ttk.Treeview`).
- **Charts:** Visualizations including wait time by hour, queue length over time, counter utilisation, table occupancy timeline, wait histogram, and the 2×2 combined summary dashboard.
- **Compare Scenarios:** Side-by-side evaluation of operational scenarios with percentage improvements, visual tradeoff bars, and automated plain-English recommendations.
- **Reports:** Export generated analytical reports (TXT/CSV) and chart image files.

### Student View
- **"Best Time to Visit" Chart:** Hourly expected wait curve indicating optimal visiting windows.
- **Fastest Counter Finder:** Interactive selector (e.g., *"I want to eat at 1:15 PM, which counter is quickest?"*).
- **Seating Availability Forecast:** Anticipated table congestion indicators.

---

## 5. Repository Structure & File Ownership

> **The Golden Rule:** Every directory and file has exactly **one owner**. Never modify a file you do not own. All inter-module communication is governed strictly by the **Shared Interface Contract**.

```text
vjti-canteen-simulation/
├── main.py                              # Owner: Aarya (launches app / CLI)
├── README.md                            # Owner: Aarya (documentation)
├── requirements.txt                     # Owner: Aarya (dependencies)
├── .gitignore                           # Owner: Aarya (git exclusions)
│
├── simulation/                          # Owner: Aarya (whole folder)
│   ├── __init__.py
│   ├── engine.py                        # CanteenSimulation time-step engine & state machine
│   ├── arrival_generator.py             # Poisson & Negative Binomial arrival generators
│   ├── scenarios.py                     # What-if scenario runners & policies
│   └── calibration.py                   # Model validation against field data
│
├── models/                              # Owner: Chaiti (whole folder)
│   ├── __init__.py
│   ├── customer.py                      # Customer entity & lifecycle states
│   ├── counter.py                       # Counter queue & server class
│   ├── menu_item.py                     # MenuItem data class & combo bundles
│   └── dining_table.py                  # Seating & dining table allocation
│
├── config/                              # Owner: Chaiti (whole folder)
│   ├── __init__.py
│   ├── canteen_config.json              # Default simulation & seating configuration
│   └── config_loader.py                 # JSON parser & validation
│
├── visualization/                       # Owner: Chaiti (whole folder)
│   ├── __init__.py
│   ├── plots.py                         # Individual Matplotlib figures (waits, tables, queues)
│   └── dashboard.py                     # 2x2 multi-panel dashboard
│
├── data/
│   ├── menu.csv                         # Owner: Chaiti (menu items with popularity weights)
│   ├── observed_arrivals.csv            # Owner: Chaiti (empirical field observation data)
│   └── logs/                            # Output simulation logs (gitignored)
│
├── data_handler/                        # Owner: Janhavi (whole folder)
│   ├── __init__.py
│   ├── file_manager.py                  # Log saving/loading & directory handling
│   ├── logger.py                        # Timestamped simulation event logger
│   └── validator.py                     # Config & input data integrity checks
│
├── analysis/                            # Owner: Janhavi (whole folder)
│   ├── __init__.py
│   ├── metrics.py                       # Pandas/NumPy statistical analysis & dwell metrics
│   ├── report_generator.py              # Text/CSV summary report generator
│   └── recommender.py                   # Cost-benefit plain-English engine (staff vs seating)
│
├── ui/                                  # Owner: Jiya (whole folder)
│   ├── __init__.py
│   ├── app.py                           # Tkinter main window & navigation
│   ├── styles.py                        # Design tokens, color palette & fonts
│   ├── input_panel.py                   # Form inputs, sliders & background thread
│   ├── results_panel.py                 # KPI cards & Treeview tables
│   ├── charts_panel.py                  # FigureCanvasTkAgg embedded view
│   ├── compare_panel.py                 # Scenario comparison tab
│   └── student_view.py                  # Student-facing optimizer view & seating forecast
│
├── outputs/                             # Auto-generated outputs (gitignored)
│   ├── charts/                          # Exported PNG/SVG charts
│   └── reports/                         # Exported text/CSV reports
│
├── tests/
│   ├── __init__.py
│   ├── dummy_customers.csv              # Owner: Janhavi (mock data for parallel work)
│   ├── test_simulation.py               # Owner: Aarya (engine tests)
│   ├── test_models_config.py            # Owner: Chaiti (models & config tests)
│   ├── test_analysis.py                 # Owner: Janhavi (metrics verification)
│   └── test_ui_helpers.py               # Owner: Jiya (UI validation tests)
│
└── docs/
    ├── 01_simulation_notes.md           # Owner: Aarya
    ├── 02_models_visualization_notes.md # Owner: Chaiti
    ├── 03_data_analysis_notes.md        # Owner: Janhavi
    └── 04_ui_notes.md                   # Owner: Jiya
```

---

## 6. Team Division & Detailed Deliverables per Member

To guarantee clear accountability and conflict-free collaboration, responsibilities and specific deliverables are partitioned strictly by member role:

### 👩‍💻 Aarya — Simulation Engine, Scenarios & Integration
- **Deliverables:**
  1. **`simulation/arrival_generator.py`**:
     - Implement time-dependent Poisson arrivals for steady-state periods.
     - Implement **Negative Binomial distribution** ($r, p$) during lunch rush (12:30 PM to 2:30 PM) to model bursty group arrivals and class-dismissal clumping.
     - Provide reproducible RNG seed control.
  2. **`simulation/engine.py`**:
     - Minute-by-minute discrete time-step simulation loop.
     - Order allocation using popularity weights and combo recognition.
     - **Seating and Table Management**: Track table occupancy, dining duration countdown, and transition customers from `Service` to `Dining` to `Departure`.
     - Output standardized DataFrame with queue wait time, dining time, and total dwell time.
  3. **`simulation/scenarios.py`**:
     - Implement scenario configurations: *Current Setup*, *Add One Counter*, *Faster Billing*, *Peak Hour Extra Staff*, and *Seating Expansion / Combo Bundles*.
     - Function `run_all_scenarios(base_config, seed)`.
  4. **`simulation/calibration.py`**:
     - Calibrate Poisson vs. Negative Binomial simulated arrivals against empirical counts from [`data/observed_arrivals.csv`](file:///data/observed_arrivals.csv) to validate goodness-of-fit.
  5. **`main.py`**, **`README.md`**, **`requirements.txt`**, **`tests/test_simulation.py`**, and **`docs/01_simulation_notes.md`**.

---

### 👩‍💻 Chaiti — Models, Configuration, Visualizations & Field Data
- **Deliverables:**
  1. **`models/menu_item.py` & `models/dining_table.py`**:
     - `MenuItem` class supporting price, prep time, popularity weight, stock limit, and combo attributes.
     - `DiningHall` / `Table` entity modeling seat capacity, table occupancy, and dining countdown.
  2. **`models/customer.py` & `models/counter.py`**:
     - `Customer` class tracking arrival, wait time, service time, dining duration, total dwell time, and balking status.
     - `Counter` class modeling queue lengths, parallel staff servers, and balking threshold limits.
  3. **`config/canteen_config.json` & `config/config_loader.py`**:
     - Editable configuration schema including counter staff counts, arrival rate schedules, table capacity (`total_tables`, `seats_per_table`, `avg_dining_time_min`), and distribution mode (`poisson` vs `negative_binomial`).
     - Robust loader with schema validation and error handling.
  4. **`data/menu.csv` & `data/observed_arrivals.csv`**:
     - Curation of 15–20 VJTI menu items with realistic prices, preparation times, and popularity probabilities.
     - Clean empirical lunch rush arrival counts across 5-minute intervals.
  5. **`visualization/plots.py` & `visualization/dashboard.py`**:
     - Matplotlib figure generators returning `Figure` objects:
       - `plot_wait_by_hour(df)`
       - `plot_queue_lengths(df)`
       - `plot_utilisation(df)`
       - `plot_wait_histogram(df)`
       - `plot_scenario_comparison(comparison_df)`
       - `plot_table_occupancy(df)` (table utilization over time)
       - `plot_dashboard(df)` (2×2 combined executive dashboard)
  6. **`tests/test_models_config.py`** and **`docs/02_models_visualization_notes.md`**.

---

### 👩‍💻 Janhavi — Data Handling, Analysis & Recommendations
- **Deliverables:**
  1. **`data_handler/file_manager.py` & `data_handler/logger.py`**:
     - Safe CSV/report read-write operations with `FileNotFoundError` and `PermissionError` handling.
     - Timestamped simulation event logger (`[13:05] Customer #42 joined Snacks queue`).
  2. **`data_handler/validator.py`**:
     - Comprehensive validation of configuration values, seating numbers, negative rates, and form inputs.
  3. **`analysis/metrics.py`**:
     - Compute core KPIs: `avg_wait`, `median_wait`, `max_wait`, `p90_wait`, `peak_queue`, `peak_queue_time`, `balking_rate`, `throughput_per_hour`, `total_revenue`, `utilisation`, and `revenue_by_counter`.
     - **Seating & Dwell Metrics**: Compute `avg_dwell_time`, `table_occupancy_pct`, and `seating_bottleneck_rate`.
     - `hourly_wait_table(df)` for student advisory view.
  4. **`analysis/recommender.py`**:
     - Plain-English recommendation engine analyzing whether **counter queues** or **table shortages** represent the primary bottleneck.
     - Cost-benefit assessment: staff wage cost vs. saved revenue from reduced balking vs. table expansion feasibility.
  5. **`analysis/report_generator.py`**:
     - Formatted text/CSV summary reports and `compare_scenarios()` matrix with percentage improvements.
  6. **`tests/dummy_customers.csv`**, **`tests/test_analysis.py`**, and **`docs/03_data_analysis_notes.md`**.

---

### 👩‍💻 Jiya — Desktop Application & User Experience
- **Deliverables:**
  1. **`ui/styles.py`**:
     - Cohesive VJTI design system: color palette, Segoe UI typography hierarchy, card frames, and customized ttk widget themes.
  2. **`ui/input_panel.py`**:
     - Parameter adjustment controls: counters count, staff per counter, peak arrival rate, balking limit, table capacity, and distribution toggle (Poisson / Negative Binomial).
     - Non-blocking background worker thread (`threading.Thread`) with progress bar.
  3. **`ui/results_panel.py`**:
     - Visual KPI cards (Avg Wait, P90 Wait, Balking %, Throughput, Revenue, Table Occupancy %, Avg Dwell Time) and counter breakdown table (`ttk.Treeview`).
  4. **`ui/charts_panel.py`**:
     - Embed Matplotlib figures into Tkinter using `FigureCanvasTkAgg`.
     - Dropdown chart switcher and "Save Chart Image" dialog.
  5. **`ui/compare_panel.py`**:
     - Scenario comparison table with percentage improvement metrics and automated recommendation display.
  6. **`ui/student_view.py`**:
     - "Best Time to Visit" chart, fastest counter recommendation, and seating availability forecast.
  7. **`ui/app.py`**, **`tests/test_ui_helpers.py`**, and **`docs/04_ui_notes.md`**.

---

## 7. Shared Interface Contract

The contract defines the integration bridge. It allows all four team members to build and test their modules independently in parallel using mock fixtures.

### 7.1 Customer Output DataFrame (`pandas.DataFrame`)

Every simulation run returns a standardized customer DataFrame with the following schema:

| Column | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | `int` | Unique sequential customer identifier |
| `arrival_time` | `int` | Minute of arrival since canteen opening ($t=0$) |
| `counter` | `str` | Name of counter joined (e.g., `"Snacks"`, `"Thali"`, `"Beverages"`) |
| `items` | `str` | Semicolon-separated list of items ordered |
| `queue_length_on_arrival` | `int` | Number of people in queue when customer arrived |
| `service_start` | `float` / `int` | Minute service began (`np.nan` if customer balked) |
| `departure` | `float` / `int` | Minute customer left counter / finished dining (`np.nan` if balked) |
| `wait_time` | `float` / `int` | Queue waiting duration: `service_start - arrival_time` (`np.nan` if balked) |
| `service_time` | `float` / `int` | Service transaction duration (`0` if balked) |
| `dining_time` | `float` / `int` | Time spent at dining table (if seated) |
| `dwell_time` | `float` / `int` | Total duration in canteen: `wait_time + service_time + dining_time` |
| `order_value` | `float` | Total monetary value of order in ₹ |
| `balked` | `bool` | `True` if customer abandoned the queue without ordering, else `False` |

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
- `avg_dwell_time`: Average total customer duration inside canteen (queue + service + dining).
- `table_occupancy_pct`: Average percentage of dining tables occupied during operating hours.

---

## 8. Git Workflow & Collaboration Rules

1. `main` is protected — no direct commits without review.
2. Dedicated feature branches for each team member:
   - `feature/aarya-simulation`
   - `feature/chaiti-models-viz`
   - `feature/janhavi-analysis`
   - `feature/jiya-ui`
3. Pull `origin/main` daily before beginning development.
4. Keep commit messages clear, descriptive, and atomic:
   - ✅ `feat(simulation): add negative binomial arrival distribution for peak burst`
   - ❌ `update`, `final`, `fixes`
5. Only touch files you own as defined in Section 5.

---

## 9. Field Data Collection (VJTI Canteen)

The simulation is calibrated against empirical data collected during peak lunch rush at the VJTI canteen:
- **Aarya:** Measured entrance arrival counts partitioned into 5-minute intervals.
- **Chaiti:** Recorded queue lengths at Snacks, Thali, and Beverage counters every 5 minutes.
- **Janhavi:** Measured service transaction times across 20+ customers using a stopwatch.
- **Jiya:** Documented menu pricing, item categories, and staff counts per counter.

The collected data is stored in [`data/observed_arrivals.csv`](file:///data/observed_arrivals.csv) and [`data/menu.csv`](file:///data/menu.csv), and used by [`simulation/calibration.py`](file:///simulation/calibration.py) to validate arrival distribution accuracy.

---

## 10. How to Install, Run & Test

### 1. Prerequisites
- Python 3.9+ (Python 3.10+ recommended)
- `pip` package manager
- Tkinter (included with standard Python on Windows/macOS; on Linux: `sudo apt-get install python3-tk`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Aarya-2601/canteen_queue_simulator.git
cd canteen_queue_simulator

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch Desktop Application
```bash
python main.py
```

### 4. Run Test Suite
```bash
python -m pytest tests/ -v
```

---

## 11. Definition of "Done"

- [x] `python main.py` opens the GUI seamlessly without runtime errors.
- [x] Simulation runs from the UI in under 10 seconds with a background thread and responsive progress bar.
- [x] All KPI cards and Matplotlib charts render dynamically inside the Tkinter canvas.
- [x] Scenario comparison tab displays percentage improvements and automated recommendations.
- [x] Student view accurately calculates the optimal visit time and quickest counter.
- [x] Input validation provides friendly dialog alerts and prevents crashes on invalid values.
- [x] Deterministic runs: identical random seed produces identical results.
- [x] Comprehensive test coverage and clear documentation for every module.

---

## 12. Viva Questions & Key Concepts

1. **Why transition from Poisson to Negative Binomial distribution?**
   While Poisson is suitable for random, independent arrivals with equal mean and variance ($\sigma^2 = \mu$), peak canteen periods exhibit **overdispersion** ($\sigma^2 > \mu$) because students arrive in groups when lectures dismiss. The Negative Binomial distribution captures this clustering effect.
2. **How do popularity weighting and item bundling speed up service?**
   Rather than treating all items identically, popularity weights assign higher probabilities to top sellers. Bundling popular pairings (e.g. Samosa Pav + Chai) allows kitchen staff to pre-assemble orders during rush hours, reducing transaction time.
3. **Why model dining tables as a separate resource from counters?**
   Students don't immediately leave after picking up food; they occupy tables. If seating capacity is reached, students linger or crowd near counters, creating a secondary bottleneck. Measuring **total dwell time** differentiates between counter delays and seating deficits.
4. **How was the model validated?**
   [`simulation/calibration.py`](file:///simulation/calibration.py) compares simulated arrival distributions with empirical samples from [`data/observed_arrivals.csv`](file:///data/observed_arrivals.csv) using goodness-of-fit and relative error metrics.
5. **Why is the 90th percentile (P90) wait time superior to the average?**
   Averages hide tail latency. An average wait of 6 minutes might sound acceptable, but a P90 of 18 minutes means 1 out of 10 students spends nearly their entire lunch break waiting.
6. **Why use threading for Tkinter simulation execution?**
   Running a long computational loop on the main Tkinter thread blocks the GUI event loop, causing the window to freeze. Running the engine in a background `threading.Thread` preserves responsiveness.

---

## 13. Stretch Goals

- [ ] Online token / pre-ordering simulation scenario.
- [ ] Export analytical summary reports as formatted PDF documents.
- [ ] Light and dark theme switcher in `styles.py`.
- [ ] Standalone command-line interface (CLI) mode via `argparse`.
- [ ] Congestion heatmap across hour × counter matrix.
