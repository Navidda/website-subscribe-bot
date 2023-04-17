import json


class PersistedList:
    """A list that persists to a file"""
    def __init__(self, filename):
        self.filename = filename
        self.items = []

    def __repr__(self):
        return f"PersistableList(items={self.items})"

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.items, f)

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.items = json.load(f)
        except FileNotFoundError:
            pass

    def append(self, item):
        if item not in self.items:
            self.items.append(item)
            self.save()

    def remove(self, item):
        try:
            self.items.remove(item)
            self.save()
        except ValueError:
            pass
