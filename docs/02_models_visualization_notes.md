# 📚 Technical Notes: Models, Configuration, Visualizations & Field Data

**Author / Component Owner:** Chaiti  
**Role:** Second Year B.Tech IT, VJTI  
**Module Scope:** `models/`, `config/`, `visualization/`, `data/menu.csv`, `data/observed_arrivals.csv`, `tests/test_models_config.py`

---

## 1. Overview & Architectural Role

As part of our four-member team mini project for the **VJTI Canteen Queue Simulator**, my responsibility encompasses:
1. **Domain Models (`models/`):** Designing the object-oriented abstractions for Customers, Counters, and Menu Items.
2. **Configuration & Loaders (`config/`):** Building editable JSON configurations and safe parsers to decouple operational parameters from simulation logic.
3. **Empirical Field Data (`data/`):** Collecting real-world observations at the VJTI canteen and creating realistic menu and arrival datasets.
4. **Visual Analytics (`visualization/`):** Developing Matplotlib figure generators and an integrated 2×2 executive dashboard for the Tkinter desktop GUI.
5. **Unit Verification (`tests/`):** Ensuring full unit test coverage for all models, configuration loaders, and plotting routines.

---

## 2. Domain Models Design (`models/`)

### 2.1 Customer Model (`models/customer.py`)
In college canteens, students do not just arrive and vanish; their journey has distinct stages. We model the customer lifecycle:

```text
[ARRIVED] ───(Queue >= Balking Limit?)───► [BALKED] (Leaves without ordering)
   │
   ▼ (Joins queue)
[WAITING IN QUEUE]
   │
   ▼ (Counter staff becomes free)
[IN_SERVICE]
   │
   ▼ (Service completed)
[DEPARTED] (Logged to output dataset)
```

#### Shared Interface Contract Compliance (Section 7.1)
The `Customer.to_dict()` method serializes customer records into the standardized dictionary schema:
- `customer_id`: Unique sequential student identifier.
- `arrival_time`: Minute customer entered the canteen ($t=0$ at start).
- `counter`: Assigned counter (`"Snacks"`, `"Thali"`, `"Beverages"`).
- `items`: Semicolon-delimited string of ordered items.
- `queue_length_on_arrival`: Queue depth observed upon arrival.
- `service_start`: Timestamp when service began (`NaN` if balked).
- `departure`: Timestamp of exit (`NaN` if balked).
- `wait_time`: Queue delay (`service_start - arrival_time`).
- `service_time`: Active service duration ($0.0$ if balked).
- `order_value`: Monetary total in ₹.
- `balked`: Boolean flag indicating abandonment.

### 2.2 Counter & Parallel Servers (`models/counter.py`)
Each counter manages:
- **FIFO Queue (`list`):** First-in, first-out ordering ensuring fair customer processing.
- **Parallel Staff Servers (`staff_count`):** Allows multiple staff members to serve customers simultaneously at the same counter.
- **Efficiency Multiplier (`efficiency_multiplier`):** Multiplier reflecting billing and preparation speedups (e.g., $1.35\times$ for barcode/UPI token screens).
- **Time Tick (`tick()`):** Decrements remaining service duration each minute and frees up staff.
- **Utilisation Tracking:** Measures cumulative busy minutes against available staff capacity:
  $$\text{Utilisation (\%)} = \frac{\text{Total Busy Minutes}}{\text{Total Simulation Duration} \times \text{staff\_count}} \times 100$$

### 2.3 MenuItem & Combo Bundling (`models/menu_item.py`)
College canteens have top-selling items and common pairings:
- **Popularity Weighting:** Every item has an empirical probability weight derived from sales frequency.
- **Stock Depletion Tracking:** Simulates afternoon stock-outs of fast-moving items like Samosa Pav or Misal Pav.
- **Pre-Packaged Combos:** Items with `is_combo = True` (such as *"Samosa Pav + Cutting Chai"*) bundle constituent items, reducing preparation time by 25–40%.

---

## 3. Configuration & Loader Design (`config/`)

### 3.1 Schema Structure (`config/canteen_config.json`)
The configuration separates simulation operational variables from executable code:
- `canteen_name`: "VJTI College Canteen".
- `simulation_minutes`: 360 (6 hours of operation).
- `random_seed`: 42 for reproducible deterministic runs.
- `default_balking_limit`: 10 students.
- `negative_binomial_r`: 4 (dispersion parameter).
- `counters`: Per-counter list defining staff count, balking tolerance, and efficiency multiplier.
- `arrival_rates`: Hourly or slot-based arrival rates for morning, lunch, and afternoon.

### 3.2 Safe Loading & Validation (`config/config_loader.py`)
- `load_config(path)`: Validates that required sections (`counters`, `arrival_rates`) and mandatory fields are present.
- `load_menu(path)`: Parses CSV records directly into a list of `MenuItem` objects, validating prices, positive preparation times, and popularity weights.

---

## 4. Empirical Field Data Collection (`data/`)

### 4.1 Collection Methodology at VJTI
Real observations were conducted during the peak college hours:
1. **Menu Data (`data/menu.csv`):** 20 canonical items from the VJTI canteen menu categorized into Snacks, Thali, Beverages, and Combos, with prices ranging from ₹10 (Cutting Chai) to ₹90 (Full Thali).
2. **Arrival Data (`data/observed_arrivals.csv`):** 60 five-minute observation intervals spanning 10:00 AM to 3:00 PM. Noticeable arrival surges occur at 12:30 PM (lecture dismissal) and 1:00 PM (lunch break), peaking at 44 arrivals / 5 minutes with queues up to 19 students at Snacks. Used directly by `calibration.py` to validate the Negative Binomial model.

---

## 5. Visualizations & Dashboard (`visualization/`)

All plotting functions create clean `matplotlib.figure.Figure` instances without relying on the interactive backend (`matplotlib.use("Agg")`). This avoids thread conflicts and integrates seamlessly with Tkinter's `FigureCanvasTkAgg`.

### 5.1 Individual Plots (`visualization/plots.py`)
1. **`plot_wait_by_hour(df)`:** Grouped bar chart comparing Average Wait vs. 90th Percentile (P90) wait times across each hour of operation.
2. **`plot_queue_lengths(df)`:** Multi-line timeline showing 5-minute binned queue depths across Snacks, Thali, and Beverage counters, with the lunch rush period highlighted in gold.
3. **`plot_utilisation(df)`:** Horizontal bar chart with an 80% congestion threshold line, distinguishing comfortable counters from overworked ones.
4. **`plot_wait_histogram(df)`:** Frequency distribution of customer wait times with annotated Average, Median, and P90 vertical reference lines.
5. **`plot_scenario_comparison(comparison_df)`:** Side-by-side grouped bar chart displaying improvements in Average Wait Time and Balking Rate across operational policies.

### 5.2 Composite Executive Dashboard (`visualization/dashboard.py`)
The `plot_dashboard(df)` function builds a 2×2 unified executive summary:
- **Top-Left:** Hourly Wait Times (Avg vs P90)
- **Top-Right:** Counter Queue Timeline
- **Bottom-Left:** Wait Time Distribution & Tail Latency
- **Bottom-Right:** Counter Staff Utilisation Rates

---

## 6. Viva Questions & Explanations (Cheat Sheet)

### Q1: Why did you choose an Object-Oriented approach for Customer and Counter?
> *"Object-Oriented Programming models real-world physical entities naturally. Each `Customer` maintains its own arrival timestamp, order items, and state. Each `Counter` maintains its own FIFO queue and staff servers. This encapsulation makes the code modular, intuitive, and clean."*

### Q2: Why is the 90th percentile (P90) wait time more important than the average?
> *"In queueing systems, averages hide tail latency. If 9 students wait 2 minutes and 1 student waits 20 minutes, the average is only 3.8 minutes. However, the P90 wait time is 20 minutes, revealing that 10% of students suffer unacceptable delays. Canteen managers must optimize for tail latency (P90) to minimize student dissatisfaction."*

### Q3: Why is Negative Binomial better than Poisson for canteen arrivals?
> *"Poisson assumes independent arrivals where variance equals the mean ($\sigma^2 = \mu$). But in a college, students arrive in bursty clumps when lecture bells ring, causing overdispersion ($\sigma^2 > \mu$). The Negative Binomial distribution captures this burstiness accurately."*

### Q4: How do pre-assembled combo bundles reduce queue delays?
> *"Analysis of sales data showed that over 25% of orders combine a snack and a beverage (e.g., Samosa Pav + Cutting Chai). By pre-packaging these combos before the lunch rush, kitchen staff save transaction and preparation time, significantly lowering queue congestion."*

### Q5: How do your Matplotlib charts render inside Tkinter without freezing the UI?
> *"We instantiate standalone `Figure` objects using Matplotlib's non-interactive `Agg` backend and pass them directly to Tkinter using `FigureCanvasTkAgg`. This prevents Tkinter window freezes and eliminates GUI thread conflicts."*
