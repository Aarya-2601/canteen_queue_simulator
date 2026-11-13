import numpy as np

class ArrivalGenerator:
    def __init__(self, rates=None, r=4, seed=None):
        if rates is None:
            self.rates = {
                "morning": {"start": 0, "end": 150, "rate": 0.8},
                "lunch": {"start": 150, "end": 240, "rate": 2.6},
                "afternoon": {"start": 240, "end": 360, "rate": 0.9}
            }
        else:
            self.rates = rates
        self.r = int(r)
        self.rng = np.random.default_rng(seed)

    def get_rate(self, t):
        for slot in self.rates.values():
            st = slot.get("start", slot.get("start_minute", 0))
            en = slot.get("end", slot.get("end_minute", 360))
            if st <= t < en:
                return float(slot.get("rate", slot.get("lambda_per_min", 1.0)))
        return 1.0

    def generate_arrivals(self, t):
        lam = self.get_rate(t)
        if lam <= 0:
            return 0
        p = self.r / (self.r + lam)
        return int(self.rng.negative_binomial(self.r, p))

    def generate_arrivals_for_minute(self, t):
        return self.generate_arrivals(t)
