class EntryExitManager:
    def __init__(self):
        self.seen = set()

    def should_trigger(self, plate, zone):
        key = f"{plate}_{zone}"

        if key in self.seen:
            return False

        self.seen.add(key)
        return True

    def reset(self, plate):
        # optional reset when car leaves completely
        to_remove = [k for k in self.seen if k.startswith(plate)]
        for k in to_remove:
            self.seen.remove(k)