import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import Enum

Callback = Callable[[], None | Awaitable[None]]


def ns_to_seconds(ns: int) -> float:
    return ns / 1_000_000_000


# Create an enum for schedule policy
class SchedulePolicy(Enum):
    FIXED_SCHEDULE = "FIXED_SCHEDULE"
    FIXED_DELAY = "FIXED_DELAY"


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

    def __init__(
        self,
        timeout: int,
        callback: Callback,
        schedule_policy: str = SchedulePolicy.FIXED_SCHEDULE.value,
    ) -> None:
        self.timeout: int = timeout
        self.callback: Callback = callback
        self.stopped: bool = False
        self.started: bool = False

        # Check if the provided schedule_policy is valid
        if schedule_policy not in SchedulePolicy.__members__:
            raise ValueError(
                f"Invalid schedule_policy: {schedule_policy}. Must be one of {[policy for policy in SchedulePolicy.__members__]}"
            )

        self.schedule_policy: SchedulePolicy = SchedulePolicy(schedule_policy)

    """
      Starts the timer loop if not already started.
      Returns True if the timer was started, False if it was already running.
    """

    async def start(self) -> bool:
        if self.started:
            return False

        self.started = True
        self.stopped = False
        await self.loop(time.monotonic_ns())
        return True

    """
      callback execution loop that runs the callback at each timeout interval
      until the timer is stopped.
      param scheduledTime: the time when the current loop iteration was scheduled.
    """

    async def loop(self, scheduledTime: int) -> None:
        if self.stopped is True:
            return

        # Supports both async and sync callbacks
        if asyncio.iscoroutinefunction(self.callback):
            await self.callback()
        else:
            self.callback()

        now: int = time.monotonic_ns()
        nextScheduledTime: int = (
            scheduledTime + self.timeout
            if self.schedule_policy == SchedulePolicy.FIXED_SCHEDULE
            else now + self.timeout
        )
        task: asyncio.Task = asyncio.create_task(
            asyncio.sleep(ns_to_seconds(nextScheduledTime - now))
        )
        task.add_done_callback(
            lambda coro_object: asyncio.create_task(self.loop(nextScheduledTime))
        )

    """
      Stops the timer if it is running.
    """

    async def stop(self) -> bool:
        if self.stopped:
            return False
        self.stopped = True
        self.started = False
        return True
