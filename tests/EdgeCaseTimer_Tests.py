import asyncio
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/asyncio_utils"))
)
from Timer import Timer


async def startAndStopTimer(timer: Timer, sleepInterval: int) -> int:
    timer.start()
    # Sleep for the specified interval
    await asyncio.sleep(sleepInterval)
    timer.stop()


class TimerTests(unittest.IsolatedAsyncioTestCase):
    async def test_timer_starts_and_stoped_before_next_tick(self):
        timeoutInSecs: int = 2
        totalTestDurationInSecs: int = 7
        expectedTics: int = totalTestDurationInSecs // timeoutInSecs - 1
        counter: int = 0

        async def increment_counter():
            print(datetime.now())
            nonlocal counter
            counter += 1

        timer: Timer = Timer(timeoutInSecs * 1_000_000_000, increment_counter)
        print(
            "Starting timer test: timeout={}s, total duration={}s, expected tics={}, time={}".format(
                timeoutInSecs, totalTestDurationInSecs, expectedTics, datetime.now()
            )
        )
        timer.start()
        await asyncio.sleep(totalTestDurationInSecs - timeoutInSecs)
        timer.stop()
        await asyncio.sleep(timeoutInSecs)

        self.assertEqual(counter, expectedTics)

    async def test_timer_starts_and_callback_overruns(self):
        timeoutInSecs: int = 1
        totalTestDurationInSecs: int = 8
        expectedTics: int = (totalTestDurationInSecs // timeoutInSecs) // 2
        counter: int = 0

        async def increment_counter():
            print(datetime.now())
            # Simulate a long-running task that overruns the next tick
            nonlocal counter
            counter += 1
            await asyncio.sleep(1.5)

        timer: Timer = Timer(timeoutInSecs * 1_000_000_000, increment_counter)
        print(
            "Starting timer test: timeout={}s, total duration={}s, expected tics={}, time={}".format(
                timeoutInSecs, totalTestDurationInSecs, expectedTics, datetime.now()
            )
        )
        timer.start()
        await asyncio.sleep(totalTestDurationInSecs)
        timer.stop()

        self.assertEqual(counter, expectedTics)
