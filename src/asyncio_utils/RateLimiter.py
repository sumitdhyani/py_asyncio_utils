import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import TypeVar


class RingBuffer:
    def __init__(self, size: int):
        self.size = size
        self.buffer: list[TypeVar("T")] = []

    def push(self, item: TypeVar("T")) -> None:
        if self.is_full():
            self.buffer.pop(0)
        self.buffer.append(item)

    def is_full(self) -> bool:
        return len(self.buffer) == self.size

    def is_empty(self) -> bool:
        return len(self.buffer) == 0

    def get_front(self) -> TypeVar("T"):
        if self.is_empty():
            raise IndexError("RingBuffer is empty")
        return self.buffer[0]


# A function returning None that can be either synchronous or asynchronous
Callback = Callable[[], None | Awaitable[None]]

"""
    Implements a rate limiter that allows a certain number of tasks to be executed
    within a specified time window.
"""


class RateLimiter:
    """
    Initializes the rate limiter with a specified rate and time window.
    param rate: the maximum number of tasks allowed in the time window.
    param per: the time window as a datetime.timedelta.
    """

    def __init__(self, rate: int, per: timedelta):
        self.ringBuffer: RingBuffer = RingBuffer(rate)
        self.rate: int = rate
        self.per: timedelta = per
        self.pendingTasks: list[Callback] = []

    def bandWidthAvailable(self) -> bool:
        return (
            not self.ringBuffer.is_full()
            or self.ringBuffer.get_front() + self.per < datetime.now()
        )

    """
        Pushes a new task to be executed under the rate limit.
        param task: a callable which can be synchronous or an async coroutine function.
    """

    async def executeAndLogTask(self, task: Callback) -> None:
        if asyncio.iscoroutinefunction(task):
            await task()
        else:
            task()
        self.ringBuffer.push(datetime.now())

    # Schedule the onBandWidthAvailable event for when bandwidth becomes available
    # i.e., when the oldest timestamp in the ring buffer + per is reached
    # i.e when t = ringBuffer.get_front() + per
    async def scheduleBandWidthAvailableEvt(self) -> None:
        asyncio.create_task(
            asyncio.sleep(
                (
                    (self.ringBuffer.get_front() + self.per) - datetime.now()
                ).total_seconds()
            )
        ).add_done_callback(
            lambda coro_object: asyncio.create_task(self.onBandWidthAvailable())
        )

    async def push(self, task: Callback) -> None:
        if len(self.pendingTasks) > 0:
            self.pendingTasks.append(task)
            return
        elif not self.bandWidthAvailable():
            # no pending tasks but bandwidth not available,
            # queue the task and schedule the next bandwidthAvailable event
            self.pendingTasks.append(task)
            await self.scheduleBandWidthAvailableEvt()
        else:
            await self.executeAndLogTask(task)

    async def onBandWidthAvailable(self) -> None:
        while self.bandWidthAvailable() and len(self.pendingTasks) > 0:
            await self.executeAndLogTask(self.pendingTasks.pop(0))

        # If the bandwidth is exhausted but there are still pending tasks,
        # schedule the next bandwidthAvailable event
        if len(self.pendingTasks) > 0:
            await self.scheduleBandWidthAvailableEvt()
