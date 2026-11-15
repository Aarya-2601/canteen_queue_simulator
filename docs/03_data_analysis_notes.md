# Data & Analysis Notes - Janhavi

## Data Handler
- file_manager.py: handles saving and loading customer logs as CSV files.
- Uses os.makedirs so missing folders in outputs/ are auto-created.
- logger.py: records events with timestamps in 24-hr format like [13:05].
- validator.py: validates DataFrame against the 11 required contract columns.
- Raises error if arrival_time or order_value contain negative numbers.

## Metrics & Calculations
- Drops balked customers before computing wait time statistics.
- Computes mean, median, max, and P90 wait time using numpy.percentile.
- P90 shows the worst 10% rush delay, which average wait usually hides.
- Balking rate: (balked customer count / total customer arrivals) * 100.
- Throughput: total served customers divided by total simulation hours.
- Utilisation: total minutes a counter was busy / total open minutes.
- Lost revenue: sum of order values from students who balked without eating.

## Reports & Recommendations
- hourly_wait_table: groups wait by hour slot for the student view tab.
- compare_scenarios: makes a summary table comparing baseline vs other setups.
- Computes percentage wait improvement against Current Setup baseline.
- save_report: exports a formatted text summary with stats and utilisation.
- recommender.py: selects optimal setup based on lowest average wait time.
- Calculates ROI: checks if recovered sales cover the Rs 300 staff wage.
- Suggests extra peak-hour staff only if net profit gain is positive.