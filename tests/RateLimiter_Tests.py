import asyncio
import os
import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/asyncio_utils"))
)
from RateLimiter import RateLimiter


class RateLimiterTests(unittest.IsolatedAsyncioTestCase):
    # Binary search to find the latest timestamp less than the threshold
    def findLatest(self, timestamps: list[datetime], threshold: datetime) -> int:
        low: int = 0
        high: int = len(timestamps) - 1
        result: int = -1
        while low <= high:
            mid: int = (low + high) // 2
            if timestamps[mid] < threshold:
                result = mid
                low = mid + 1
            else:
                high = mid - 1
        return result

    # Binary search to find the earliest timestamp greater than the threshold
    def findEarliest(self, timestamps: list[datetime], threshold: datetime) -> int:
        low: int = 0
        high: int = len(timestamps) - 1
        result: int = -1
        while low <= high:
            mid: int = (low + high) // 2
            if timestamps[mid] > threshold:
                result = mid
                high = mid - 1
            else:
                low = mid + 1
        return result

    async def test_1(self):
        await self.do_test(1000, 100, timedelta(seconds=1))

    async def test_2(self):
        await self.do_test(10000, 1000, timedelta(seconds=1))

    async def do_test(self, totalTasks: int, rate: int, per: timedelta):
        print(
            f"Running RateLimiter test: totalTasks={totalTasks}, rate={rate}, per={per}"
        )
        rateLimiter: RateLimiter = RateLimiter(rate, per)
        executionLog: list[datetime] = []

        async def log_execution():
            nonlocal executionLog
            executionLog.append(datetime.now())

        # Push 1000 tasks
        for _ in range(totalTasks):
            await rateLimiter.push(log_execution)
        # Wait enough time for all tasks to complete
        await asyncio.sleep((totalTasks // rate) * per.total_seconds() + 1)
        self.assertEqual(len(executionLog), totalTasks)

        # Check that no more than 'rate' tasks were executed in any 'per' time window
        for i in range(totalTasks - rate + 1, rate):
            self.assertLessEqual(executionLog[i + rate - 1] - executionLog[i], rate)

        # Check that there is at least 'per' time difference a task and the task 'rate' positions before it
        for i in range(totalTasks - rate):
            self.assertGreater(executionLog[i + rate] - executionLog[i], per)

        startWindow: datetime = executionLog[0]
        endWindow: datetime = executionLog[-1]

        currStart: datetime = startWindow
        cuurrEnd: datetime = currStart + timedelta(seconds=1)

        # Slide a 'per' timeimeinterval window across the entire execution log, 1 ms at a time
        # and check there were never more than 'rate' executions in that window
        while cuurrEnd <= endWindow:
            startIdx: int = self.findEarliest(executionLog, currStart)
            endIdx: int = self.findLatest(executionLog, cuurrEnd)
            if startIdx == -1:
                startIdx = 0
            self.assertLessEqual(endIdx - startIdx + 1, rate)
            currStart += timedelta(milliseconds=1)
            cuurrEnd += timedelta(milliseconds=1)
