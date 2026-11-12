# Simulation Notes - Aarya

## Arrival Generator
- Uses Negative Binomial distribution instead of Poisson.
- Parameters: r (dispersion) and p = r / (r + lambda).
- This models student group arrivals and rush spikes when lectures end.

## Simulation Engine
- Discrete minute-by-minute loop.
- In each minute:
  1. Generate arrivals using Negative Binomial.
  2. Customers pick counter (Snacks, Thali, Beverages).
  3. If queue length is greater than or equal to limit, customer balks.
  4. Free staff take next customer in line.
  5. Active counters count down service time.
  6. Departing customers are recorded in DataFrame.

## Scenarios
- Current Setup: baseline configuration.
- Add One Counter: adds an express counter.
- Faster Billing: increases counter efficiency by 35%.
- Peak Hour Extra Staff: adds +1 staff to busy counters.
