"""
models/customer.py - Customer entity for student lifecycle in canteen.
Owner: Chaiti
"""


class Customer:
    """Tracks a student's queue arrival, waiting, service, and balking."""

    def __init__(self, customer_id, arrival_time, counter="Snacks", items="",
                 queue_length_on_arrival=0, balking_threshold=10, order_value=0.0,
                 service_time=0.0, **kwargs):
        self.customer_id = int(customer_id)
        self.arrival_time = int(arrival_time)
        self.counter = str(counter)
        self.items = items if isinstance(items, str) else ";".join(str(i) for i in items)
        self.queue_length_on_arrival = int(queue_length_on_arrival)
        self.balking_threshold = int(balking_threshold)
        self.order_value = float(order_value)
        self.service_time = float(service_time)

        self.service_start = kwargs.get("service_start", None)
        self.departure = kwargs.get("departure", None)
        self.wait_time = kwargs.get("wait_time", None)
        self.balked = False
        self._prep = 2.0

    def check_balk(self, current_queue_length):
        """Returns True if student leaves due to long queue."""
        self.queue_length_on_arrival = int(current_queue_length)
        if self.queue_length_on_arrival >= self.balking_threshold:
            self.balked = True
            self.wait_time = float("nan")
            self.service_start = float("nan")
            self.departure = float("nan")
            self.service_time = 0.0
            return True
        return False

    def start_service(self, current_time):
        """Marks service start timestamp and computes wait time."""
        self.service_start = float(current_time)
        self.wait_time = max(0.0, float(current_time - self.arrival_time))

    def complete_service(self, current_time):
        """Marks service completion timestamp."""
        self.departure = float(current_time)

    def to_dict(self):
        """Converts customer record to standardized dictionary row."""
        return {
            "customer_id": self.customer_id,
            "arrival_time": self.arrival_time,
            "counter": self.counter,
            "items": self.items,
            "queue_length_on_arrival": self.queue_length_on_arrival,
            "service_start": float("nan") if self.balked else (self.service_start or float("nan")),
            "departure": float("nan") if self.balked else (self.departure or float("nan")),
            "wait_time": float("nan") if self.balked else (self.wait_time or 0.0),
            "service_time": 0.0 if self.balked else float(self.service_time),
            "order_value": round(float(self.order_value), 2),
            "balked": bool(self.balked),
        }

    def __repr__(self):
        return f"Customer(#{self.customer_id}, t={self.arrival_time}, {self.counter})"
