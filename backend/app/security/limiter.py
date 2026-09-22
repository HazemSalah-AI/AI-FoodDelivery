from collections import OrderedDict, deque
from threading import Lock
from time import monotonic

from app.core.errors import DomainError


class AuthLimiter:
    """Bounded, process-local throttle. Production proxy supplies additional rate limits."""

    def __init__(self):
        self.entries = OrderedDict()
        self.lock = Lock()

    def check(self, key):
        with self.lock:
            current = monotonic()
            values = self.entries.pop(key, deque())
            while values and values[0] <= current - 60:
                values.popleft()
            self.entries[key] = values
            while len(self.entries) > 5000:
                self.entries.popitem(last=False)
            if len(values) >= 20:
                raise DomainError(429, "rate_limited", "Too many attempts. Try again in a minute.")
            values.append(current)
