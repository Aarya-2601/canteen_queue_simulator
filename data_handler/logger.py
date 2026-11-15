class SimulationLogger:
    def __init__(self, start_hour=10):
        self.start_hour = start_hour
        self.logs = []

    def log(self, minute, msg):
        # convert minute offset to 24-hr time
        hr = (self.start_hour + minute // 60) % 24
        mn = minute % 60
        entry = f"[{hr:02d}:{mn:02d}] {msg}"
        self.logs.append(entry)
        return entry

    def save(self, file_path):
        with open(file_path, "w") as f:
            f.write("\n".join(self.logs))