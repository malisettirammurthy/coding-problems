import re
from dataclasses import dataclass
from typing import Optional
from collections import defaultdict
from pprint import pprint
import statistics

@dataclass
class LogEntry:
    timestamp: str
    level: str
    service: str
    latency_ms: Optional[float]
    status: str
    message: str


class LogParser:
    def __init__(self):
        self.regex_pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\slevel=(\w+)\sservice=(\w+)\slatency_ms=(\d+)\sstatus=(\w+)"
    
    def parse_line(self, line):
        grps = re.match(self.regex_pattern, line)
        # print(line)
        if grps:
            grps = grps.groups()
        if not grps or len(grps) != 5:
            return None
        return LogEntry(
                timestamp=grps[0],
                level=grps[1],
                service=grps[2],
                latency_ms=grps[3],
                status=grps[4],
                message=line.strip()
        )

    def parse_lines(self, lines):
        entries = []
        for line in lines:
            entry = self.parse_line(line)
            
            if entry:
                entries.append(entry)
        return entries
"""
service_log_metrics = {
    'redis': {
        'latencies': [],      # just the float values
        'total': 0,
        'error_count': 0,
    }
}
"""

def default_svc_metrics():
    return {"latencies":[], "total":0, "error_count":0}

class MetricsAggregator:
    def __init__(self):
        self.service_log_metrics = defaultdict(default_svc_metrics)
    
    def ingest(self, entry):
        svc = entry.service
        latency=int(entry.latency_ms)
        status=entry.status
        self.service_log_metrics[svc]['latencies'].append(latency)
        self.service_log_metrics[svc]['total'] += 1
        if status == 'error':
            self.service_log_metrics[svc]['error_count'] += 1

    
    def percentile(self, data, p):
        if not data:
            return 0
        sorted_data = sorted(data)
        ix = int(len(sorted_data) * p / 100)
        return sorted_data[min(ix, len(sorted_data) -1)]


    def report(self):
        result = {}
        for svc in self.service_log_metrics:
            total = self.service_log_metrics[svc]['total']
            latencies = self.service_log_metrics[svc]['latencies']
            error_rate = round(self.service_log_metrics[svc]['error_count'] / total, 4) if total else 0
            result[svc] = {
                'total_requests': total,
                'error_rate': error_rate,
                'p50_ms': self.percentile(latencies, 50),
                'p95_ms': self.percentile(latencies, 95),
                'p99_ms': self.percentile(latencies, 99),
                'avg_ms': round(statistics.mean(latencies), 2) if latencies else 0,
            }
        return result


lines = """2024-03-25T10:00:01Z level=INFO service=postgres latency_ms=12 status=ok
2024-03-25T10:00:02Z level=ERROR service=postgres latency_ms=5000 status=error
2024-03-25T10:00:03Z level=INFO service=redis latency_ms=1 status=ok
2024-03-25T10:00:04Z level=WARN service=mysql latency_ms=300 status=ok
2024-03-25T10:00:05Z level=ERROR service=redis latency_ms=800 status=error
2024-03-25T10:00:06Z level=INFO service=postgres latency_ms=25 status=ok
2024-03-25T10:00:07Z level=INFO service=mysql latency_ms=90 status=ok
2024-03-25T10:00:08Z level=ERROR service=postgres latency_ms=4200 status=error
2024-03-25T10:00:09Z level=INFO service=redis latency_ms=2 status=ok
2024-03-25T10:00:10Z level=WARN service=mysql latency_ms=450 status=error"""

parser = LogParser()
aggregator = MetricsAggregator()
for entry in parser.parse_lines(lines.splitlines()):
    aggregator.ingest(entry)

pprint(aggregator.service_log_metrics)
pprint(aggregator.report())

