import asyncio
import time
from collections.abc import Awaitable, Callable
from enum import Enum

Callback = Callable[[], None | Awaitable[None]]
ErrCallback = Callable[[Exception], None]


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
    param timeout_ns: interval between ticks in nanoseconds.
    param callback: a callable which can be synchronous or an async coroutine function.

    started / stopped: booleans used to prevent double-starts and to signal stopping.
    """

    def __init__(
        self,
        timeout_ns: int,
        callback: Callback,
        err_callback: ErrCallback | None = None,
        schedule_policy: str = "FIXED_SCHEDULE",
    ) -> None:
        if timeout_ns <= 0:
            raise ValueError("timeout_ns must be a positive integer")

        self.timeout_ns: int = timeout_ns
        self.callback: Callback = callback
        self.err_callback: ErrCallback | None = err_callback
        self.stopped: bool = False
        self.started: bool = False
        self.background_sleep_task: asyncio.Task | None = None

        try:
            # Check if the provided schedule_policy is valid
            self.schedule_policy: SchedulePolicy = SchedulePolicy(schedule_policy)
        except ValueError:
            raise ValueError(
                f"Invalid schedule_policy: {schedule_policy}. Must be one of {[policy.value for policy in SchedulePolicy]}"
            )

    """
      Starts the timer loop if not already started.
      Returns True if the timer was started, False if it was already running.
    """

    def start(self) -> bool:
        if self.started:
            return False

        self.started = True
        self.stopped = False
        now: int = time.monotonic_ns()
        scheduled_time: int = now + self.timeout_ns

        self.background_sleep_task = asyncio.create_task(
            asyncio.sleep(ns_to_seconds(scheduled_time - now))
        )

        self.background_sleep_task.add_done_callback(
            lambda coro_object, st=scheduled_time: asyncio.create_task(self.loop(st))
            # This may happen if the stop method is called before background_sleep_task completes
            if not coro_object.cancelled()
            else None
        )
        return True

    """
      callback execution loop that runs the callback at each timeout interval
      until the timer is stopped.
      param scheduledTime: the time when the current loop iteration was scheduled.
    """

    async def loop(self, scheduled_time: int) -> None:
        self.background_sleep_task = None

        if self.stopped:
            return

        try:
            result: None | Awaitable[None] = self.callback()

            # Supports both async and sync callbacks
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            if self.err_callback is not None:
                self.err_callback(e)
            else:
                raise e

        now: int = time.monotonic_ns()
        next_scheduled_time: int = (
            scheduled_time + self.timeout_ns
            if self.schedule_policy == SchedulePolicy.FIXED_SCHEDULE
            else now + self.timeout_ns
        )

        # If the task overruns, schedule next execution based on current time
        while next_scheduled_time <= now:
            next_scheduled_time += self.timeout_ns

        self.background_sleep_task = asyncio.create_task(
            asyncio.sleep(ns_to_seconds(next_scheduled_time - now))
        )

        self.background_sleep_task.add_done_callback(
            lambda coro_object, st=next_scheduled_time: asyncio.create_task(
                self.loop(st)
            )
            if not coro_object.cancelled()
            else None
        )

    """
      Stops the timer if it is running.
    """

    def stop(self) -> bool:
        if self.stopped or not self.started:
            return False

        self.stopped = True
        self.started = False

        if self.background_sleep_task is not None:
            self.background_sleep_task.cancel()

        return True
