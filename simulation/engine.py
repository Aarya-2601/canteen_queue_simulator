import numpy as np
import pandas as pd
from models.counter import Counter
from models.customer import Customer
from simulation.arrival_generator import ArrivalGenerator

class CanteenSimulation:
    def __init__(self, cfg, seed=None):
        self.cfg = cfg
        self.seed = seed
        if self.seed is None:
            self.seed = cfg.get("random_seed", 42)
        self.rng = np.random.default_rng(self.seed)
        self.total_time = int(cfg.get("simulation_minutes", 360))
        r_val = cfg.get("negative_binomial_r", 4)
        self.gen = ArrivalGenerator(cfg.get("arrival_rates"), r=r_val, seed=self.seed)

        self.counters = {}
        for c in cfg.get("counters", []):
            name = c["name"]
            st = c.get("staff_count", 1)
            eff = c.get("efficiency_multiplier", 1.0)
            balk = c.get("balking_queue_limit", cfg.get("default_balking_limit", 10))
            self.counters[name] = Counter(name, staff_count=st, efficiency_multiplier=eff, balking_queue_limit=balk)

        if len(self.counters) == 0:
            self.counters["Snacks"] = Counter("Snacks", staff_count=2, balking_queue_limit=10)
            self.counters["Thali"] = Counter("Thali", staff_count=2, balking_queue_limit=8)
            self.counters["Beverages"] = Counter("Beverages", staff_count=1, balking_queue_limit=8)

        self.customers = []
        self.cust_id = 0

    def _sample_order(self, counter_name):
        c_name = counter_name.lower()
        if "snack" in c_name:
            items = [("Samosa Pav", 20.0, 1.2), ("Vada Pav", 18.0, 1.0), ("Misal Pav", 45.0, 2.5), ("Masala Dosa", 50.0, 3.5), ("Veg Sandwich", 35.0, 2.0)]
        elif "thali" in c_name or "meal" in c_name:
            items = [("Mini Thali", 60.0, 2.2), ("Special VJTI Thali", 90.0, 3.2), ("Veg Fried Rice", 70.0, 3.5)]
        else:
            items = [("Cutting Chai", 12.0, 0.8), ("Special Masala Chai", 15.0, 1.0), ("Filter Coffee", 20.0, 1.2), ("Cold Coffee", 35.0, 1.5)]

        num_items = 1
        if self.rng.random() > 0.4:
            num_items = 2

        idx = self.rng.choice(len(items), size=num_items, replace=True)
        names = []
        total_price = 0.0
        total_prep = 0.0
        for i in idx:
            names.append(items[i][0])
            total_price += items[i][1]
            total_prep += items[i][2]

        return ";".join(names), total_price, max(1.0, total_prep * 0.8)

    def _choose_counter(self):
        names = list(self.counters.keys())
        if len(names) == 1:
            return names[0]
        weights = []
        for n in names:
            nl = n.lower()
            if "snack" in nl:
                weights.append(0.50)
            elif "thali" in nl or "meal" in nl:
                weights.append(0.30)
            elif "bev" in nl:
                weights.append(0.20)
            else:
                weights.append(0.25)
        total_w = sum(weights)
        norm_w = [w / total_w for w in weights]
        return str(self.rng.choice(names, p=norm_w))

    def run(self, progress_cb=None):
        for t in range(self.total_time):
            n_arr = self.gen.generate_arrivals(t)
            for _ in range(n_arr):
                self.cust_id += 1
                c_name = self._choose_counter()
                counter = self.counters[c_name]
                item_str, price, prep = self._sample_order(c_name)

                cust = Customer(
                    customer_id=self.cust_id,
                    arrival_time=t,
                    counter=c_name,
                    items=item_str,
                    queue_length_on_arrival=counter.queue_length()
                )
                cust.order_value = price
                cust._prep = prep

                counter.add_to_queue(cust)
                self.customers.append(cust)

            for counter in self.counters.values():
                while counter.is_free() and len(counter.queue) > 0:
                    nxt = counter.queue[0]
                    dur = getattr(nxt, "_prep", 2.0)
                    counter.assign_next_customer(t, base_service_duration=dur)
                counter.tick(t)

            if progress_cb and (t % 15 == 0 or t == self.total_time - 1):
                pct = int(((t + 1) / self.total_time) * 100)
                progress_cb(pct)

        rows = []
        for c in self.customers:
            rows.append(c.to_dict())
        return pd.DataFrame(rows)

def run_simulation(cfg, seed=None, progress_callback=None):
    sim = CanteenSimulation(cfg, seed=seed)
    return sim.run(progress_cb=progress_callback)
