import asyncio
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/asyncio_utils"))
)

from Timer import Timer


# Basic Timer Example
# This example demonstrates how to use the Timer to execute a callback function at regular intervals.
# In this example, we create a Timer that triggers every 1 second and prints the current datetime.
# The timer runs for 10.5 seconds before stopping.
# the console output will show the timer callback being executed every second.
async def basic_timer_example():
    tickNumber: int = 0

    def callback() -> None:
        nonlocal tickNumber
        tickNumber += 1
        print(f"Timer callback executed at {datetime.now()}, tick {tickNumber}")

    timer: Timer = Timer(
        timedelta(seconds=1),
        callback,
    )
    await timer.start()
    # Let the timer run for 10.5 seconds
    # The timer callback should trigger 11 times
    await asyncio.sleep(10.5)
    await timer.stop()


asyncio.run(basic_timer_example())
