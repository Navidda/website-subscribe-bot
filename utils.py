import json


class PersistedList:
    """A list that persists to a file"""

    def __init__(self, filename):
        self.filename = filename
        self.items = []
        self.load()

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

    def pop(self, index=0):
        item = self.items.pop(index)
        self.save()
        return item

    def remove(self, item):
        try:
            self.items.remove(item)
            self.save()
        except ValueError:
            pass


class PersistableDict:
    """A dict that persists to a file"""

    def __init__(self, filename, default_value=None):
        self.filename = filename
        self.data = {}
        self.load()
        if self.data == {}:
            self.data = default_value
            self.save()

    def __repr__(self):
        return f"PersistableDict(items={self.data})"

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f)

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass


class Persistable:
    """Base class for persistable objects"""

    def __init__(self, filename, default_value=None):
        self.filename = filename
        self.data = None
        self.load()
        if self.data is None and default_value is not None:
            self.data = default_value
            self.save()

    def __repr__(self):
        return f"Persistable(filename={self.filename})"

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f)

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            pass
