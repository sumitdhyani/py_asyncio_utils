# py_asyncio_utils

**Overview**
- **Library:** A collection of asyncio-friendly utilities for Python focusing on simple timing and rate-limiting primitives.
- **Purpose:** Provide lightweight building blocks to schedule repeated work (`Timer`) and to limit throughput of concurrent tasks (`RateLimiter`) in asyncio programs.

**class Timer**
- **File:** [src/asyncio_utils/Timer.py](src/asyncio_utils/Timer.py)
- **What it does:** Implements a repeating, async-friendly timer that calls a user-provided callback at a fixed interval until stopped. Callbacks may be synchronous functions or async coroutines.
- **API (high-level):**
  - `Timer(timeout: datetime.timedelta, callback: Callable)` — create a timer with a repeat interval and callback.
  - `await start()` — start the timer loop (non-blocking; schedules repeated executions).
  - `await stop()` — stop the timer loop.

- **Example:**
```py
import asyncio
from datetime import timedelta
from asyncio_utils.Timer import Timer

async def my_async_callback():
    print('tick')

timer = Timer(timedelta(seconds=2), my_async_callback)
asyncio.run(timer.start())  # starts the repeating timer
# ... later: await timer.stop()
```

**RateLimiter**
- **File:** [src/asyncio_utils/RateLimiter.py](src/asyncio_utils/RateLimiter.py)
- **What it does:** Enforces a maximum number of executions (a rate) per time window. Tasks pushed to the limiter are executed as bandwidth becomes available. Tasks may be synchronous functions or async coroutines.
- **API (high-level):**
  - `RateLimiter(rate: int, per: datetime.timedelta)` — allow `rate` executions per `per` interval.
  - `await push(task: Callable)` — enqueue a task; it will run when allowed.
- **Notes:** Internally uses a small ring buffer of recent execution timestamps and a pending queue. When the buffer is full, execution is deferred until the earliest timestamp ages out by `per`.
- **Example:**
```py
import asyncio
from datetime import timedelta
from asyncio_utils.RateLimiter import RateLimiter

async def work():
    print('did work')

rate_limiter = RateLimiter(10, timedelta(seconds=1))

async def produce():
    for _ in range(50):
        await rate_limiter.push(work)

asyncio.run(produce())
```
For concrete examples, showing actual working code using these classes, see the example code in the `examples/` directory.

## Working Examples
- [examples/BasicRateLimiterExample.py](examples/BasicRateLimiterExample.py) — basic `RateLimiter` usage.
- [examples/BasicTimerExample.py](examples/BasicTimerExample.py) — basic `Timer` usage.
- [examples/MultipleRateLimitersExample.py](examples/MultipleRateLimitersExample.py) — using multiple `RateLimiter` instances.
- [examples/MultipleTimersExample.py](examples/MultipleTimersExample.py) — using multiple `Timer` instances.

**Build package from source**
- The project uses `pyproject.toml`. To build distribution archives install `build` and run:

```bash
pip install --upgrade build
python -m build
```

- The above produces a `dist/` folder with `.whl` and `.tar.gz` files. You can also install locally with:

```bash
pip install .        # install from source
pip install -e .     # editable install for development
```

- Alternatively, this repository includes `build_package.py`; you can run it if you prefer (it wraps standard build steps):

```bash
python build_package.py
```

**Run tests**
- The tests are in the `tests/` directory and use `unittest`'s async test support. You can run them with `unittest` or with `pytest`.

Run with unittest (cross-platform):
```bash
python -m unittest discover -v
```

Run with pytest (if installed):
```bash
pip install pytest
pytest -q
```

- Platform-specific helper scripts are provided:
  - Windows: `run_tests.bat`
  - Unix/macOS: `run_tests.sh`

**Notes & troubleshooting**
- The utilities depend only on Python's standard library (`asyncio`, `datetime`, etc.). Tests use `unittest.IsolatedAsyncioTestCase` which requires Python 3.8+.
- If you see timing-sensitive failures, they may be due to scheduling resolution on the host system — increase sleep durations in tests when diagnosing on slow/oversubscribed CI runners.

---
For code, see the implementation files: [src/asyncio_utils/Timer.py](src/asyncio_utils/Timer.py) and [src/asyncio_utils/RateLimiter.py](src/asyncio_utils/RateLimiter.py).
