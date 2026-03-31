from dataclasses import dataclass
import time
import threading


# ─────────────────────────────────────────────
# A real connection object (simulated)
# ─────────────────────────────────────────────

@dataclass
class Connection:
    conn_id: int

    def execute(self, query: str) -> str:
        time.sleep(2)   # simulate query work
        return f"[conn-{self.conn_id}] result of: {query}"

def thread_name():
    return threading.current_thread().name


# ─────────────────────────────────────────────
# Step 2: Semaphore + _free list + _lock
#
# Semaphore  — same as before, controls HOW MANY enter
# _free      — the actual connection objects to hand out
# _lock      — makes pop() from _free safe (one thread at a time)
# ─────────────────────────────────────────────

class ConnectionPool:
    def __init__(self, max_connections: int = 3):
        self._semaphore = threading.Semaphore(max_connections)
        self._lock      = threading.Lock()
        self._free      = [Connection(conn_id=i+1) for i in range(max_connections)]

        print(f"[Pool] Ready — {len(self._free)} connections: "
              f"{[f'conn-{c.conn_id}' for c in self._free]}")

    def acquire(self) -> Connection:
        name = thread_name()
        print(f"[{name}] waiting for permit...")

        self._semaphore.acquire()          # ← same as before, blocks if full

        print(f"[{name}] GOT permit — picking connection...")

        with self._lock:                   # ← NEW: safely pop from _free
            conn = self._free.pop()
            print(f"[{name}] picked conn-{conn.conn_id}  "
                  f"| _free now: {[f'conn-{c.conn_id}' for c in self._free]}")

        return conn                        # ← NEW: hand the actual object back

    def release(self, conn: Connection) -> None:
        name = thread_name()

        with self._lock:                   # ← NEW: safely append back to _free
            self._free.append(conn)
            print(f"[{name}] returned conn-{conn.conn_id} "
                  f"| _free now: {[f'conn-{c.conn_id}' for c in self._free]}")

        self._semaphore.release()          # ← same as before, unblocks a waiter
        print(f"[{name}] released permit")


# ─────────────────────────────────────────────
# Worker — now actually uses the connection
# ─────────────────────────────────────────────

def worker(pool: ConnectionPool, query: str):
    conn = pool.acquire()                  # blocks until permit + connection
    try:
        result = conn.execute(query)
        print(f"[{thread_name()}] {result}")
    finally:
        pool.release(conn)                 # ALWAYS return it, even on exception


# ── run it ────────────────────────────────────
pool = ConnectionPool(max_connections=3)
print()

# ── run it ────────────────────────────────────
pool = ConnectionPool(max_connections=3)
print()

threads = [
    threading.Thread(
        target=worker,
        args=(pool, f"SELECT * FROM orders WHERE id={i}"),
        name=f"T{i}"
    )
    for i in range(6)
]

for t in threads:
    t.start()
for t in threads:
    t.join()





