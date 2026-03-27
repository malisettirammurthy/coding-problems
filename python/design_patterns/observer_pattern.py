"""
Observer - Notify multiple subscribers on events.
Use when: One event should trigger multiple independent reactions.
"""
from abc import ABC, abstractmethod

class EvenListner(ABC):
    @abstractmethod
    def on_event(self, event_type, payload):
        pass


class AlertingListner(EvenListner):
    def on_event(self, event_type, payload):
        if event_type == 'db.failed':
            print(f"Alert: {payload['db_id']} failed, paging on-call")


class BillingListener(EvenListner):
    def on_event(self, event_type, payload):
        if event_type == 'db.provisioned':
            print(f"Billing: {payload['db_id']} provisioned, start metering.")


class EventBus():
    def __init__(self):
        self.listners = []
    
    def subscribe(self, listner):
        self.listners.append(listner)

    def publish(self, event_type, payload):
        for _listner in self.listners:
            _listner.on_event(event_type, payload)

# Usage
bus = EventBus()
bus.subscribe(BillingListener())
bus.subscribe(AlertingListner())
bus.publish('db.provisioned', {'db_id': 'pg-001', 'team': 'payments'})

bus.publish('db.failed', {'db_id': 'pg-002', 'team': 'monitoring'})
