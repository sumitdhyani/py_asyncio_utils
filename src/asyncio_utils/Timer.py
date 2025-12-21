import asyncio
from collections.abc import Callable, Awaitable
from datetime import datetime, timedelta

Callback = Callable[[], None | Awaitable[None]]

"""
  Implements a repeating async-friendly timer that calls a provided function at a fixed
  timeout interval until stopped.
"""
class Timer:
  
    """
      Stores the timeout and the callback function and initializes two flags:
      param timeout: intended as a datetime.timedelta that represents the interval between runs.
      param callback: a callable which can be synchronous or an async coroutine function.
    
      started / stopped: booleans used to prevent double-starts and to signal stopping.
    """
    def __init__(self, timeout: timedelta, callback: Callback):
      self.timeout = timeout
      self.callback = callback
      self.stopped = False
      self.started = False

    """
      Starts the timer loop if not already started.
      Returns True if the timer was started, False if it was already running.
    """
    async def start(self) -> bool:
        if self.started:
          return False

        self.started = True
        self.stopped = False
        await self.loop(datetime.now())
        return True
        
    """
      callback execution loop that runs the callback at each timeout interval
      until the timer is stopped.
      param scheduledTime: the datetime when the current loop iteration was scheduled.
    """
    async def loop(self, scheduledTime : datetime) -> None:
      if self.stopped is True:
        return

      # Supports both async and sync callbacks
      if asyncio.iscoroutinefunction(self.callback):
        await self.callback()
      else:
        self.callback()
      
      nextScheduledTime : datetime = scheduledTime + self.timeout
      task : asyncio.Task = asyncio.create_task(asyncio.sleep((nextScheduledTime - datetime.now()).total_seconds()))
      task.add_done_callback(lambda coro_object: asyncio.create_task(self.loop(nextScheduledTime)))

    """
      Stops the timer if it is running.
    """    
    async def stop(self) -> bool:
      if self.stopped:
          return False
      self.stopped = True
      self.started = False
      return True