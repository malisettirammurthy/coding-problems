"""
Design and implement following 3 metric types.

Counter:
    - Tracks a value that only ever goes up. Ex: total number of provisioning req received, total errors.

Gauge:
    - Tracks a value that can go up or down. Ex: Current number of active database connections, current storage usage in DB.

Histogram:
    - Tracks the distribution of a measure value.
    - Ex: Query latency in ms, backup duration in seconds.

Requirements:
Counter:
    - Must support increment(amount) -- default amount is 1. Should reject -ve values.
Gauge:
    - Must support set(value), increment(amount), decrement(amount).
Histogram:
    - Must support observe(value) to record a measurement, amd must be able to return P50, P95, P99 on demand.

Common to all 3:
    - snapshot() - current state as a plain dict. This is what gets scraped by Prometheus.
    - Should support reset() method.
    - There must be a MetricsRegisty - A central place where metrics are registered and retrieved by name.
        It should be Singleton.

Sample usage your code must support:
    registry = MetricsRegistry.get_instance()

    provision_requests = registry.counter("db_provision_requests_total")
    provision_requests.increment()
    provision_requests.increment(5)

    active_connections = registry.gauge("db_active_connections")
    active_connections.set(47)
    active_connections.increment(3)
    active_connections.decrement(10)

    query_latency = registry.histogram("db_query_latency_ms")
    query_latency.observe(12)
    query_latency.observe(142)
    query_latency.observe(4500)

    print(registry.collect_all())
""" 

'''
**The full picture before we code:**
```
Metric (abstract base)
│   name: str
│   snapshot() -> dict   ← abstract
│   reset()              ← abstract
│
├── Counter
│       _value: float
│       increment(amount)
│
├── Gauge
│       _value: float
│       set(value)
│       increment(amount)
│       decrement(amount)
│
└── Histogram
        _observations: list[float]
        observe(value)
        percentile(p) → sorts on read, O(n log n)

MetricsRegistry  (separate, not a Metric)
    _instance          ← class variable, singleton guard
    _metrics: dict     ← instance variable, name → Metric object
    get_instance()     ← classmethod
    counter(name)
    gauge(name)
    histogram(name)
    collect_all()

'''
import math
from abc import ABC, abstractmethod
import random
import threading

#
class Metric(ABC):
    def __init__(self, name):
        self.name = name
        self._lock = threading.Lock()

    @abstractmethod
    def snapshot(self):
        pass

    @abstractmethod
    def reset(self):
        pass

#
class Counter(Metric):
    def __init__(self, metric_name):
        super().__init__(metric_name)   # ← this sets self.name on the base class
        self._value = 0.0

    def increment(self, amount=1):
        if amount < 0:
            raise ValueError("Counter can only increment - use Gauge for values to support decrement.")
        with self._lock:
            self._value += amount

    def snapshot(self):
        return {'name': self.name,
                'type': 'counter',
                'value': self._value}

    def reset(self):
        with self._lock:
            self._value = 0.0


#
class Gauge(Metric):
    def __init__(self, metric_name):
        super().__init__(metric_name)   # ← this sets self.name on the base class
        self._value = 0.0
    
    def set(self, value):
        with self._lock:
            self._value = value
    
    def increment(self, amount=1):
        with self._lock:
            self._value += amount

    def decrement(self, amount=1):
        with self._lock:
            self._value -= amount

    def snapshot(self):
        return {'name': self.name,
                'type': 'gauge',
                'value': self._value}

    def reset(self):
        with self._lock:
            self._value = 0.0
#
class Histogram(Metric):
    def __init__(self, name):
        super().__init__(name)   # ← this sets self.name on the base class
        self.observations = []
    
    def observe(self, value):
        with self._lock:
            self.observations.append(value)

    def percentile(self, p):
        if not self.observations:
            return 0.0
        _sorted_data = sorted(self.observations)
        ix = math.floor(len(_sorted_data) * p / 100)
        print(f"Index: {ix} for percenile: {p}, data_len: {len(_sorted_data)}")
        return min(_sorted_data[ix], len(_sorted_data) - 1)

    def snapshot(self):
        return {'name': self.name,
                'type': 'histogram',
                'count': len(self.observations),
                'p50': self.percentile(50),
                'p95': self.percentile(95),
                'p99': self.percentile(99),
                }

    def reset(self):
        with self._lock:
            self.observations = []

#
class MetricsRegistry():
    _instance = None
    _class_lock = threading.Lock()     # separate lock for singleton creation

    def __init__(self):
        self._metrics = {} #name: metric object.
        self._lock = threading.Lock()  # lock for registry writes

    @classmethod
    def get_instance(cls):
        with cls._class_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def counter(self, name):
        with self._lock:
            if name in self._metrics:
                metric_obj = self._metrics[name]
            else:
                metric_obj = Counter(name)
                self._metrics[name] = metric_obj
        return metric_obj

    def gauge(self, name):
        with self._lock:
            if name in self._metrics:
                metric_obj = self._metrics[name]
            else:
                metric_obj = Gauge(name)
                self._metrics[name] = metric_obj
        return metric_obj

    def histogram(self, name):
        with self._lock:
            if name in self._metrics:
                metric_obj = self._metrics[name]
            else:
                metric_obj = Histogram(name)
                self._metrics[name] = metric_obj
        return metric_obj

    def collect_all(self):
        with self._lock:
            for m, m_obj in self._metrics.items():
                data = m_obj.snapshot()
                # print(f"name: {data['name']}, type: {data['type']}, value: {data['value']}")
                print(data)

    def reset(self):
        with self._lock:
            for m, m_obj in self._metrics.items():
                pre_values = f"Resetting: {m_obj.snapshot()}"
                m_obj.reset()
                print(f"{pre_values} to {m_obj.snapshot()}")


registry = MetricsRegistry.get_instance()
provision_requests = registry.counter("db_provision_requests_total")
provision_requests.increment()
provision_requests.increment(5)
# registry.collect_all()

active_connections = registry.gauge("db_active_connections")
active_connections.set(47)
active_connections.increment(3)
active_connections.decrement(10)

query_latency = registry.histogram("db_query_latency_ms")
query_latency.observe(12)
query_latency.observe(142)
query_latency.observe(4500)
for x in range(150):
    query_latency.observe(random.randint(50, 5000))

registry.collect_all()
# registry.reset()


