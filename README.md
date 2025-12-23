# py_asyncio_utils

Deterministic, asyncio-native utilities for **timing** and **rate limiting**, designed for **predictable behavior and correctness**, not maximum throughput.

## Overview

This library provides:
- A **Timer** with explicit drift and overrun semantics
- A **RateLimiter** with serialized, sliding-window-like execution guarantees

It is intentionally conservative and explicit, making it suitable for protecting external systems (APIs, databases, hardware) where **bursts and ambiguity are unacceptable**.

## Why this library exists

Most asyncio utilities:
- implicitly drift over time
- allow bursts by default
- rely on best-effort timing
- do not clearly specify stop or overrun behavior

**py_asyncio_utils** takes a different approach:

> Behavior is explicit, testable, and deterministic — even if that costs some throughput.

---

## Installation

```bash
pip install py-asyncio-utils
```

---

## Timer

### Guarantees

- Callbacks never execute concurrently
- Stop semantics are deterministic
- Drift behavior is explicitly configurable
- Overrun behavior is well-defined and tested

### What it does

Implements a repeating, async-friendly timer that calls a user-provided callback at a fixed interval until stopped. Callbacks may be synchronous functions or async coroutines.

### API

- `Timer(timeout: datetime.timedelta | float, callback: Callable, schedule_policy: SchedulePolicy = SchedulePolicy.FIXED)` — create a timer with a repeat interval, callback, and drift policy.
- `await start()` — start the timer loop (non-blocking; schedules repeated executions).
- `await stop()` — stop the timer loop.

### Drift / Schedule Policy

Timers can be scheduled in two fundamentally different ways.

#### Fixed Schedule (drift-free)

```
next_tick = initial_start + N × interval
```

- Anchored to the original schedule
- Prevents long-term drift
- Suitable for:
  - heartbeats
  - simulations
  - clock-aligned tasks

```python
from asyncio_utils import Timer, SchedulePolicy
from datetime import timedelta

async def my_async_callback():
    print('tick')

timer = Timer(
    timedelta(seconds=2),
    my_async_callback,
    schedule_policy=SchedulePolicy.FIXED
)
await timer.start()  # starts the repeating timer
# ... later: await timer.stop()
```

#### Fixed Delay (completion-relative)

```
next_tick = callback_completion + interval
```

- Guarantees spacing between executions
- Suitable for:
  - retries
  - polling
  - cooldowns
  - background maintenance

```python
from asyncio_utils import Timer, SchedulePolicy
from datetime import timedelta

timer = Timer(
    timedelta(seconds=2),
    my_async_callback,
    schedule_policy=SchedulePolicy.DELAY
)
await timer.start()
```

### Overrun Behavior

If a callback takes longer than the interval:
- Missed ticks are not executed retroactively
- The timer resumes according to its schedule policy

This avoids burst execution and keeps behavior predictable.

### Stop Semantics

Calling `stop()` guarantees:
- No further callbacks will be executed
- Any internally scheduled wakeups exit immediately

### Example

```python
import asyncio
from datetime import timedelta
from asyncio_utils import Timer, SchedulePolicy

async def my_async_callback():
    print('tick')

async def main():
    timer = Timer(timedelta(seconds=2), my_async_callback)
    await timer.start()  # starts the repeating timer
    await asyncio.sleep(10)
    await timer.stop()

asyncio.run(main())
```

---

## RateLimiter

### Guarantees

- Serialized execution (no concurrent callbacks)
- Completion-based rate limiting
- No more than `rate` task completions occur in any `per` interval
- No bursts
- FIFO ordering

### What it does

Enforces a maximum number of executions (a rate) per time window. Tasks pushed to the limiter are executed as bandwidth becomes available. Tasks may be synchronous functions or async coroutines. Internally uses a small ring buffer of recent execution timestamps and a pending queue. When the buffer is full, execution is deferred until the earliest timestamp ages out by `per`.

### API

- `RateLimiter(rate: int, per: datetime.timedelta | float)` — allow `rate` executions per `per` interval.
- `await push(task: Callable)` — enqueue a task; it will run when allowed.

### Example

```python
import asyncio
from datetime import timedelta
from asyncio_utils import RateLimiter

async def work():
    print('did work')

async def main():
    rate_limiter = RateLimiter(10, timedelta(seconds=1))
    for _ in range(50):
        await rate_limiter.push(work)

asyncio.run(main())
```

### Important Semantic Note

This is **not** a token-bucket or admission-based limiter.

The RateLimiter enforces:

> At most `rate` task *completions* per `per` interval, with serialized execution.

This means:
- Tasks are awaited
- Long-running tasks reduce throughput
- No task executes concurrently with another

This design favors correctness and predictability over raw throughput.

### Suitable Use Cases

- Protecting external APIs
- Throttling database writes
- IO-bound pipelines
- Any system where bursts are harmful

### What this RateLimiter is NOT

- Not a token bucket
- Not burst-tolerant
- Not admission-based
- Not suitable for CPU-bound parallel work

If you need those semantics, consider **aiolimiter**.

---

## Comparison with Other Libraries

### Rate Limiting

| Library | Model | Bursts | Concurrency |
|---------|-------|--------|-------------|
| py_asyncio_utils | Serialized, completion-based | No | No |
| aiolimiter | Token bucket | Yes | Yes |

### Timers

| Library | Drift Control | Stop Semantics |
|---------|---|---|
| py_asyncio_utils | Explicit | Deterministic |
| async-timer | Implicit | Best-effort |

---

## Design Philosophy

- Prefer explicit semantics over implicit behavior
- Favor determinism over throughput
- Make edge cases testable, not accidental

---

## When to Use This Library

**Use py_asyncio_utils if:**
- You care about correctness and predictability
- You want to reason about timing behavior precisely
- You are protecting fragile downstream systems

**Do not use it if:**
- You need maximum throughput
- You rely on bursts
- You want parallel execution

---

## Working Examples

For concrete examples showing actual working code using these classes, see the example code in the `examples/` directory:

- [examples/BasicRateLimiterExample.py](examples/BasicRateLimiterExample.py) — basic `RateLimiter` usage
- [examples/BasicTimerExample.py](examples/BasicTimerExample.py) — basic `Timer` usage
- [examples/MultipleRateLimitersExample.py](examples/MultipleRateLimitersExample.py) — using multiple `RateLimiter` instances
- [examples/MultipleTimersExample.py](examples/MultipleTimersExample.py) — using multiple `Timer` instances
- [examples/SchedulePolicyTimerExample.py](examples/SchedulePolicyTimerExample.py) — using `SchedulePolicy` with `Timer`

---

## Build Package from Source

The project uses `pyproject.toml`. To build distribution archives install `build` and run:

```bash
pip install --upgrade build
python -m build
```

The above produces a `dist/` folder with `.whl` and `.tar.gz` files. You can also install locally with:

```bash
pip install .        # install from source
pip install -e .     # editable install for development
```

Alternatively, this repository includes `build_package.py`; you can run it if you prefer (it wraps standard build steps):

```bash
python build_package.py
```

---

## Run Tests

The tests are in the `tests/` directory and use `unittest`'s async test support. You can run them with `unittest` or with `pytest`.

Run with unittest (cross-platform):
```bash
python -m unittest discover -v
```

Run with pytest (if installed):
```bash
pip install pytest
pytest -q
```

Platform-specific helper scripts are provided:
- Windows: `run_tests.bat`
- Unix/macOS: `run_tests.sh`

---

## Notes & Troubleshooting

- The utilities depend only on Python's standard library (`asyncio`, `datetime`, etc.). Tests use `unittest.IsolatedAsyncioTestCase` which requires Python 3.8+.
- If you see timing-sensitive failures, they may be due to scheduling resolution on the host system — increase sleep durations in tests when diagnosing on slow/oversubscribed CI runners.

---

## License

MIT
