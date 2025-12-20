import asyncio
from datetime import datetime, timedelta
import unittest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/asyncio_utils')))
from RateLimiter import RateLimiter

class RateLimiterTests(unittest.IsolatedAsyncioTestCase):
    async def test_basic(self):
      rateLimiter : RateLimiter = RateLimiter(100, timedelta(seconds=1))
      executionLog : list[datetime] = []
      async def log_execution():
        nonlocal executionLog
        executionLog.append(datetime.now())
      # Push 1000 tasks
      for _ in range(1000):
        await rateLimiter.push(log_execution)
      # Wait enough time for all tasks to complete
      await asyncio.sleep(11)
      self.assertEqual(len(executionLog), 1000)
      for i in range(901, 100):
        self.assertLessEqual((executionLog[i+99] - executionLog[i]).total_seconds(), 1.0)
      for i in range(900):
        self.assertGreater((executionLog[i+100] - executionLog[i]).total_seconds(), 1.0)