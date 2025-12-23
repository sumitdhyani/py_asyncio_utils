import asyncio
import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/asyncio_utils"))
)
from Timer import Timer


async def startAndStopTimer(timer: Timer, sleepInterval: int) -> int:
    await timer.start()
    # Sleep for the specified interval
    await asyncio.sleep(sleepInterval)
    await timer.stop()


class TimerTests(unittest.IsolatedAsyncioTestCase):
    async def test_timer_starts_and_stoped_before_next_tick(self):
        timeoutInSecs: float = 2
        totalTestDurationInSecs: int = 7
        expectedTics: int = totalTestDurationInSecs // timeoutInSecs
        counter: int = 0

        async def increment_counter():
            print(datetime.now())
            nonlocal counter
            counter += 1

        timer: Timer = Timer(timedelta(seconds=timeoutInSecs), increment_counter)
        print(
            "Starting timer test: timeout={}s, total duration={}s, expected tics={}, time={}".format(
                timeoutInSecs, totalTestDurationInSecs, expectedTics, datetime.now()
            )
        )
        await timer.start()
        await asyncio.sleep(totalTestDurationInSecs - timeoutInSecs)
        await timer.stop()
        await asyncio.sleep(timeoutInSecs)

        self.assertEqual(counter, expectedTics)
