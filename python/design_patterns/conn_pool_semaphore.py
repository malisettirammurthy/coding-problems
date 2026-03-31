import threading
import time

# ─────────────────────────────────────────────
# Step 1: Semaphore-only pool
# No _free list, no _lock.
# Semaphore just controls HOW MANY threads
# can be "inside" the pool at once.
# ─────────────────────────────────────────────

class SimplePool:
    def __init__(self, max_connections: int = 3):
        self._semaphore = threading.Semaphore(max_connections)
        print(f"[Pool] Ready — {max_connections} permits")

    def acquire(self):
        print(f"[{thread_name()}] waiting for permit...")
        self._semaphore.acquire()          # blocks if count == 0
        print(f"[{thread_name()}] GOT permit — doing work")

    def release(self):
        self._semaphore.release()          # returns the permit
        print(f"[{thread_name()}] released permit")


def thread_name():
    return threading.current_thread().name


def worker(pool: SimplePool):
    pool.acquire()
    time.sleep(2)          # simulate query work
    pool.release()


# ── run it ────────────────────────────────────
pool = SimplePool(max_connections=3)

threads = [
    threading.Thread(target=worker, args=(pool,), name=f"T{i}")
    for i in range(6)       # 6 threads, only 3 permits
]

for t in threads:
    t.start()
for t in threads:
    t.join()