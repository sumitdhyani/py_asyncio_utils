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
    await timer.start()
    # Sleep for the specified interval
    await asyncio.sleep(sleepInterval)
    await timer.stop()


class TimerTests(unittest.IsolatedAsyncioTestCase):
    async def test_timer_starts_and_stops(self):
        timeoutInSecs: float = 1.5
        totalTestDurationInSecs: int = 7
        expectedTics: int = 1 + (totalTestDurationInSecs // timeoutInSecs)
        counter: int = 0

        async def increment_counter():
            print(datetime.now())
            nonlocal counter
            counter += 1

        timer: Timer = Timer(int(timeoutInSecs * 1_000_000_000), increment_counter)
        print(
            "Starting timer test: timeout={}s, total duration={}s, expected tics={}, time={}".format(
                timeoutInSecs, totalTestDurationInSecs, expectedTics, datetime.now()
            )
        )
        await startAndStopTimer(timer, totalTestDurationInSecs)
        self.assertEqual(counter, expectedTics)

    async def test_timer_starts_and_stops_and_restarts(self):
        timeoutInSecs: float = 1.5
        totalTestDurationInSecs: int = 7
        expectedTics: int = 1 + (totalTestDurationInSecs // timeoutInSecs)
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
        await startAndStopTimer(timer, totalTestDurationInSecs)
        self.assertEqual(counter, expectedTics)
        await asyncio.sleep(5)
        totalTestDurationInSecs: int = 11
        expectedTics: int = 1 + (totalTestDurationInSecs // timeoutInSecs)
        counter = 0
        print(
            "Restarting timer test: timeout={}s, total duration={}s, expected tics={}, time={}".format(
                timeoutInSecs, totalTestDurationInSecs, expectedTics, datetime.now()
            )
        )
        await startAndStopTimer(timer, totalTestDurationInSecs)
        self.assertEqual(counter, expectedTics)

    async def test_multiple_timers(self):
        timeoutInSecs: list[int] = [1, 2, 3]
        totalTestDurationInSecs: float = 13.5

        expectedTics: list[int] = [
            1 + (totalTestDurationInSecs // t) for t in timeoutInSecs
        ]
        counter: list[int] = [0] * len(timeoutInSecs)

        def increment_counter(idx: int):
            print(datetime.now())
            nonlocal counter
            counter[idx] += 1

        timers: list[Timer] = [
            Timer(
                timeoutInSecs[i] * 1_000_000_000,
                lambda idx=i: increment_counter(idx),
            )
            for i in range(len(timeoutInSecs))
        ]
        [
            print(
                "Starting multiple timers test: timeout={}, expected tics={}, total duration={}s".format(
                    timeoutInSecs[i], expectedTics[i], totalTestDurationInSecs
                )
            )
            for i in range(len(timeoutInSecs))
        ]
        await asyncio.gather(
            *(startAndStopTimer(timer, totalTestDurationInSecs) for timer in timers)
        )

        for i in range(len(timers)):
            self.assertEqual(counter[i], expectedTics[i])

    # Test for FIXED_DELAY schedule policy
    async def test_fixed_delay_timer(self):
        timeoutInSecs: int = 1
        taskDelayInSecs: float = 0.5
        totalTestDurationInSecs: int = 7
        expectedTics: int = 1 + (
            totalTestDurationInSecs // (timeoutInSecs + taskDelayInSecs)
        )
        counter: int = 0

        async def increment_counter():
            nonlocal counter
            counter += 1
            await asyncio.sleep(taskDelayInSecs)

        timer: Timer = Timer(
            timeoutInSecs * 1_000_000_000,
            increment_counter,
            schedule_policy="FIXED_DELAY",
        )
        print(
            "Starting FIXED_DELAY timer test: timeout={}s, total duration={}s, expected tics={}, time={}".format(
                timeoutInSecs, totalTestDurationInSecs, expectedTics, datetime.now()
            )
        )
        await startAndStopTimer(timer, totalTestDurationInSecs)
        self.assertEqual(counter, expectedTics)
