import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/asyncio_utils"))
)

from Timer import Timer


# The Fixed Schedule Timer Example
# In this example, we create a Timer that triggers every 1 second and prints the current datetime,
# with a fixed schedule policy.
# The timer runs for 10 seconds before stopping.
# The callback function simulates a workload by sleeping for 0.5 seconds.
# To compoensate for the workload delay, the timer sleeps for 0.5 seconds after the callback completes,
# instead of waiting for the full interval like in the FIXED_DELAY policy.
# As a result, the console output will show the timer callback being executed every 1 seconds,
# ticking a total of 11 times.
async def fixed_schedule_policy_timer_example():
    tickNumber: int = 0

    async def callback() -> None:
        nonlocal tickNumber
        tickNumber += 1
        print(f"Timer tick {tickNumber}, startTime={datetime.now()}")
        await asyncio.sleep(0.5)
        print(f"Timer tick {tickNumber}, endTime={datetime.now()}")

    timer: Timer = Timer(
        1_000_000_000,
        callback,
    )
    await timer.start()
    # Let the timer run for 10.5 seconds
    # The timer callback should trigger 11 times
    await asyncio.sleep(10.5)
    await timer.stop()


# The Fixed Delay Timer Example
# In this example, we create a Timer that triggers every 1 second and prints the current datetime,
# with a fixed delay schedule policy.
# The timer runs for 10 seconds before stopping.
# The callback function simulates a workload by sleeping for 0.5 seconds.
# in the default schedule policy, the timer would attempt to maintain a consistent interval between callbacks,
# but with FIXED_DELAY, each callback is scheduled to occur a fixed delay after the previous task completes.
# As a result, the console output will show the timer callback being executed every 1.5 seconds,
# ticking a total of 7 times.
async def fixed_delay_timer_example():
    tickNumber: int = 0

    async def callback() -> None:
        nonlocal tickNumber
        tickNumber += 1
        print(f"Timer tick {tickNumber}, startTime={datetime.now()}")
        await asyncio.sleep(0.5)
        print(f"Timer tick {tickNumber}, endTime={datetime.now()}")

    timer: Timer = Timer(1_000_000_000, callback, schedule_policy="FIXED_DELAY")
    await timer.start()
    # Let the timer run for 10 seconds
    # The timer callback should trigger 7 times
    await asyncio.sleep(10)
    await timer.stop()


async def demo_schedule_policies():
    print("Starting Fixed Schedule Policy Timer Example")
    await fixed_schedule_policy_timer_example()
    print("\nStarting Fixed Delay Timer Example")
    await fixed_delay_timer_example()


asyncio.run(demo_schedule_policies())
