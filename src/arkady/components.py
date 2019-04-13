# coding: utf-8

"""
A Component represents a fundamental unit of
interface and should generally map to a logical unit of control. This could be
interaction with an actual physical device or peripheral such as a sensor, a
motor, an Arduino, a DMX controller, etc. Or it could be something more virtual
such as a set of system calls, internet/intranet queries, a managed subprocess
and more.

Two basic device patterns are implemented: `SerialComponent` and `AsyncComponent`.
Use of `SerialComponent` is recommended when the underlying work must
be strictly serial (meaning non-parallel). `AsyncComponent` is suitable when
multiple executions of the `handler` can safely run simultaneously.
"""

import asyncio
import concurrent.futures
from functools import partial
import uuid


class Component(object):
    """
    The Base Component from which all other devices derive, whether they have
    synchronous or asynchronous underlying work.
    """
    def __init__(self, *args, loop=None, **kwargs):
        if loop is None:
            raise Exception('loop was not explicitly passed!')
        self.loop = loop
        self.jobs_meta = {}
        self.jobs = asyncio.Queue()

    async def requests_runner(self):
        """
        Responsible for taking jobs out of the jobs queue and executing them.

        Not implemented in this base class, must be overridden.

        :return:
        """
        raise NotImplementedError

    async def _handler(self,
                       msg=None,
                       headers=None,
                       return_queue=None,
                       topic=None,
                       ):
        """
        Scheduled as a task on the loop by listeners, this method is responsible
        for registering and queuing a call to handler as a job.
        :param msg:
        :param headers:
        :param return_queue:
        :param topic:
        :return:
        """
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


class SerialComponent(Component):
    def __init__(self, *args, **kwargs):
        super(SerialComponent, self).__init__(*args, **kwargs)
        # self.port = port
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    # Gets run as a coroutine
    async def requests_runner(self):
        while True:
            handler, meta_id = await self.jobs.get()
            if meta_id is not None:  # We expect to send a reply
                headers, return_queue = self.jobs_meta.pop(meta_id)
                reply = await self.loop.run_in_executor(self.executor, handler)
                if reply is None:  # If we get a None return, just acknowledge completion
                    reply = 'ACK'
                await return_queue.put(headers + [reply.encode('utf-8')])
            else:
                await self.loop.run_in_executor(self.executor, handler)

    def handler(self, msg: str, *args, **kwargs) -> str:
        # Shall raise an error if called without implementation
        raise NotImplementedError


class AsyncComponent(Component):
    def __init__(self, *args, **kwargs):
        super(AsyncComponent, self).__init__(*args, **kwargs)

    # The task unit, we handle wrapping normal funcs and coros
    async def enqueue(self, func, meta_id=None):
        if meta_id is None:  # No reply needed
            if asyncio.iscoroutinefunction(func.func):
                await func()
            else:
                await self.loop.run_in_executor(None, func)
        else:  # We should send back a reply
            if asyncio.iscoroutinefunction(func.func):
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


class DummySerialDevice(SerialComponent):
    def handler(self, msg: str, *args, **kwargs) -> str:
        if 'topic' in kwargs:
            print(kwargs['topic'])
        print(msg)
        return msg


class DummyAsyncDevice(AsyncComponent):
    def handler(self, msg: str, *args, **kwargs) -> str:
        if 'topic' in kwargs:
            print(kwargs['topic'])
        print(msg)
        return msg
