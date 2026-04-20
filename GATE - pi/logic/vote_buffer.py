from collections import Counter

class VoteBuffer:
    def __init__(self, max_size=7):
        self.buffer = []
        self.max_size = max_size

    def add(self, text):
        if text:
            self.buffer.append(text)

        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def is_ready(self):
        return len(self.buffer) >= 5

    def get_final(self):
        if not self.buffer:
            return None

        return Counter(self.buffer).most_common(1)[0][0]

    def clear(self):
        self.buffer = []