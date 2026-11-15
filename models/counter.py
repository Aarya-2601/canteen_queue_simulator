"""
models/counter.py - Counter class with queue, staff, and service logic.
Owner: Chaiti
"""


class Counter:
    """Represents a food service counter with staff servers and a waiting queue."""

    def __init__(self, name, staff_count=1, efficiency_multiplier=1.0, balking_queue_limit=10, **kwargs):
        self.name = str(name)
        self.staff_count = max(1, int(kwargs.get("num_staff", staff_count)))
        self.efficiency_multiplier = max(0.1, float(kwargs.get("efficiency", efficiency_multiplier)))
        self.balking_queue_limit = max(1, int(kwargs.get("balking_limit", balking_queue_limit)))

        self.queue = []  # Waiting students
        self.active_customers = []  # [{"customer": c, "remaining": float}]
        self.total_served = 0
        self.total_balked = 0
        self.total_revenue = 0.0
        self.busy_minutes = 0.0

    def queue_length(self):
        """Current number of students in queue."""
        return len(self.queue)

    def is_free(self):
        """Checks if any staff member is idle."""
        return len(self.active_customers) < self.staff_count

    def add_to_queue(self, customer):
        """Adds customer to queue, or flags balking if queue is full."""
        if len(self.queue) >= self.balking_queue_limit:
            customer.balked = True
            customer.wait_time = float("nan")
            customer.service_start = float("nan")
            customer.departure = float("nan")
            customer.service_time = 0.0
            self.total_balked += 1
            return False
        self.queue.append(customer)
        return True

    def assign_next_customer(self, current_time, base_service_duration=2.0):
        """Pulls next student from queue and begins service."""
        if not self.queue or not self.is_free():
            return
        customer = self.queue.pop(0)
        customer.service_start = float(current_time)
        customer.wait_time = max(0.0, float(current_time - customer.arrival_time))

        dur = max(1.0, round(float(base_service_duration) / self.efficiency_multiplier, 1))
        customer.service_time = dur
        self.active_customers.append({"customer": customer, "remaining": dur})

    def tick(self, current_time):
        """Advances time by 1 minute, completing orders when timer hits 0."""
        self.busy_minutes += len(self.active_customers)
        completed, remaining = [], []

        for item in self.active_customers:
            item["remaining"] -= 1.0
            if item["remaining"] <= 0:
                cust = item["customer"]
                cust.departure = float(current_time + 1)
                self.total_served += 1
                self.total_revenue += float(getattr(cust, "order_value", 0.0))
                completed.append(cust)
            else:
                remaining.append(item)

        self.active_customers = remaining
        return completed

    def step(self, current_time=0):
        """Convenience method combining staff assignment and time advance."""
        while self.is_free() and len(self.queue) > 0:
            nxt = self.queue[0]
            dur = getattr(nxt, "_prep", 2.0)
            self.assign_next_customer(current_time, base_service_duration=dur)
        return self.tick(current_time)

    def utilisation(self, total_minutes=360.0):
        """Returns staff utilisation percentage."""
        total_time = max(1.0, float(total_minutes or 360.0))
        return min(100.0, round((self.busy_minutes / (self.staff_count * total_time)) * 100.0, 1))

    def __repr__(self):
        return f"Counter('{self.name}', staff={self.staff_count}, queue={self.queue_length()})"
