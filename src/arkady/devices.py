# coding: utf-8

"""
"""

import asyncio
import concurrent.futures
from functools import partial


class Device(object):
    """
    The Base Device from which all other devices derive, whether they have
    synchronous or asynchronous underlying communication.
    """
    def __init__(self, *args, **kwargs):
        self.loop = asyncio.get_event_loop()
        self.jobs_meta = {}
        self.jobs = asyncio.Queue()

    async def requests_runner(self):
        raise NotImplementedError

    async def _handler(self,
                       msg=None,
                       headers=None,
                       return_queue=None,
                       topic=None,
                       ):
        meta_id = None
        if headers is not None:
            meta_id = uuid.uuid4()
            self.jobs_meta[meta_id] = (headers, return_queue)

        if topic is not None:
            handler = partial(self.handler, msg=msg, topic=topic)
        else:
            handler = partial(self.handler, msg=msg)
        await self.jobs.put((handler, meta_id))

    def handler(self, msg: str) -> str:
        raise NotImplementedError


class SerialDevice(Device):
    def __init__(self, port, *args, **kwargs):
        super(SerialDevice, self).__init__(*args, **kwargs)
        self.port = port
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    # Gets run as a coroutine
    async def requests_runner(self):
        while True:
            handler, meta_id = await self.jobs.get()
            if meta_id is not None:  # We expect to send a reply
                headers, return_queue = self.jobs_meta.pop(meta_id)
                reply = await self.loop.run_in_executor(self.executor, handler)
                await return_queue.put(headers + [reply.encode('utf-8')])
            else:
                await self.loop.run_in_executor(self.executor, handler)

    def handler(self, msg: str) -> str:
        # Shall raise an error if called without implementation
        raise NotImplementedError


class AsyncDevice(Device):
    def __init__(self, *args, **kwargs):
        super(AsyncDevice, self).__init__(*args, **kwargs)

    # The task unit, we handle wrapping normal funcs and coros
    async def enqueue(self, func, meta_id=None):
        if meta_id is None:  # No reply needed
            if asyncio.iscoroutinefunction(func):
                await func()
            else:
                await self.loop.run_in_executor(None, func)
        else:  # We should send back a reply
            if asyncio.iscoroutinefunction(func):
                reply = await func()
            else:
                reply = await self.loop.run_in_executor(None, func)
            if reply is None:  # If we get a None return, just acknowledge completion
                reply = 'ACK'
            headers, return_queue = self.jobs_meta.pop(meta_id)
            await return_queue.put(headers + [reply.encode('utf-8')])

    # Gets run as a coroutine
    async def requests_runner(self):
        while True:
            handler, meta_id = await self.jobs.get()
            # Just turn jobs into tasks
            self.loop.create_task(self.enqueue(handler, meta_id))
            # if meta_id is not None:  # We expect to send a reply
            #     headers, return_queue = self.jobs_meta.pop(meta_id)
            #     self.loop.create_task(self.enqueue(handler, headers, return_queue))


class DummySerialDevice(SerialDevice):
    def handler(self, msg):
        print(msg)
        return 'ACK: {}'.format(msg)
