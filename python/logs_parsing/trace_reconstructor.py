from pprint import pprint
"""
spans = [
    {"span_id": "s1", "trace_id": "t1", "parent_span_id": None,  "service": "api-gateway",        "operation": "provision_db",     "start_ms": 0,   "end_ms": 120},
    {"span_id": "s2", "trace_id": "t1", "parent_span_id": "s1",  "service": "lifecycle-controller","operation": "validate_request", "start_ms": 5,   "end_ms": 30},
    {"span_id": "s3", "trace_id": "t1", "parent_span_id": "s1",  "service": "lifecycle-controller","operation": "provision_storage","start_ms": 31,  "end_ms": 100},
    {"span_id": "s4", "trace_id": "t1", "parent_span_id": "s3",  "service": "k8s-operator",        "operation": "create_pvc",       "start_ms": 35,  "end_ms": 95},
    {"span_id": "s5", "trace_id": "t1", "parent_span_id": "s3",  "service": "k8s-operator",        "operation": "create_statefulset","start_ms": 40, "end_ms": 90},
    {"span_id": "s6", "trace_id": "t1", "parent_span_id": "s1",  "service": "telemetry-service",   "operation": "register_metrics", "start_ms": 101, "end_ms": 115},
]
```

**Your task:**

1. Parse the flat list into a tree structure, where each node knows its children
2. Print the tree with indentation showing parent-child relationships like this:
```
api-gateway.provision_db (120ms)
  lifecycle-controller.validate_request (25ms)
  lifecycle-controller.provision_storage (69ms)
    k8s-operator.create_pvc (60ms)
    k8s-operator.create_statefulset (50ms)
  telemetry-service.register_metrics (14ms)
"""

from dataclasses import dataclass, field
from typing import Optional

spans = [
    {"span_id": "s1", "trace_id": "t1", "parent_span_id": None,  "service": "api-gateway",        "operation": "provision_db",     "start_ms": 0,   "end_ms": 120},
    {"span_id": "s2", "trace_id": "t1", "parent_span_id": "s1",  "service": "lifecycle-controller","operation": "validate_request", "start_ms": 5,   "end_ms": 30},
    {"span_id": "s3", "trace_id": "t1", "parent_span_id": "s1",  "service": "lifecycle-controller","operation": "provision_storage","start_ms": 31,  "end_ms": 100},
    {"span_id": "s4", "trace_id": "t1", "parent_span_id": "s3",  "service": "k8s-operator",        "operation": "create_pvc",       "start_ms": 35,  "end_ms": 95},
    {"span_id": "s5", "trace_id": "t1", "parent_span_id": "s3",  "service": "k8s-operator",        "operation": "create_statefulset","start_ms": 40, "end_ms": 90},
    {"span_id": "s6", "trace_id": "t1", "parent_span_id": "s1",  "service": "telemetry-service",   "operation": "register_metrics", "start_ms": 101, "end_ms": 115},
]

@dataclass
class Span:
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    service: str
    operation: str
    start_ms: int
    end_ms: int

    @property
    def duration_ms(self):
        return self.end_ms - self.start_ms

@dataclass
class SpanNode:
    span: Span
    children: list

class TraceReconstructor:
    def build_tree(self, spans):
        nodes = {s.span_id: SpanNode(span=s, children=[]) for s in spans}
        # print(nodes)
        root = None
        for span in spans:
            if span.parent_span_id is None:
                root = nodes[span.span_id]
            elif span.parent_span_id in nodes:
                # nodes[span.parent_span_id].children.append(nodes[span.span_id])
                # nodes[span.parent_span_id].children.append(span)
                nodes[span.parent_span_id].children.append(nodes[span.span_id])
        return root


    def critical_path(self, node):
        if not node.children: return [node.span]
        slowest = max(node.children, key=lambda c: self._max_end(c))
        return [node.span] + self.critical_path(slowest)
    
    def _max_end(self, node):
        if not node.children: return node.span.end_ms
        return max(self._max_end(c) for c in node.children)

    def total_duration(self, node):
        return root.span.end_ms - root.span.start_ms

    def print_tree(self, node, indent=0):
        prefix = "    " * indent
        print(f"{prefix}{node.span.service}.{node.span.operation} ({node.span.duration_ms}ms)")
        for child in node.children:
            self.print_tree(child, indent + 1)


t = TraceReconstructor()
_spans = []
for _s in spans:
    span = Span(
        span_id=_s['span_id'],
        trace_id=_s['trace_id'],
        parent_span_id=_s['parent_span_id'],
        service=_s['service'],
        operation=_s['operation'],
        start_ms=_s['start_ms'],
        end_ms=_s['end_ms'],
    )
    _spans.append(span)

root = t.build_tree(_spans)
pprint(root)
# print(t.critical_path(root))
print("Total Duration:", t.total_duration(root))
t.print_tree(root)

