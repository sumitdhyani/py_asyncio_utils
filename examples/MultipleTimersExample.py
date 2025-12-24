import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/asyncio_utils"))
)

# Multiple Timers Example
# This example demonstrates how to use multiple Timer instances to execute callback functions at regular intervals.
# In this example, we create three Timer instances with different intervals:
# - Timer_1: triggers every 1 second
# - Timer_2: triggers every 2 seconds
# - Timer_3: triggers every 3 seconds
# The console output will show that each timer's callback is executed at its respective interval.
from collections.abc import Callable

from Timer import Timer

Callback = Callable[[], None]


async def multi_timer_example():
    tickNumber: list[int] = [0] * 3

    def make_callback(i: int) -> Callback:
        def callback() -> None:
            nonlocal tickNumber
            tickNumber[i] += 1
            print(
                f"Timer_{i + 1} callback executed at {datetime.now()}, tick {tickNumber[i]}"
            )

        return callback

    timers: list[Timer] = [
        Timer(
            (i + 1) * 1_000_000_000,
            make_callback(i),
        )
        for i in range(3)
    ]

    for timer in timers:
        await timer.start()

    # Let the timers run for 12.5 seconds
    # Timer_1 should trigger 13 times, Timer_2, 7 times and Timer_3, 5 times
    await asyncio.sleep(12.5)

    for timer in timers:
        await timer.stop()


asyncio.run(multi_timer_example())
