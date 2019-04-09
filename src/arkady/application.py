# coding: utf-8

"""

"""

import asyncio
import zmq
import zmq.asyncio
from .listeners import router, sub
from functools import partial


class Application(object):
    def __init__(self, loop=None):
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self.zmq_context = zmq.asyncio.Context()
        self.api_map = {}
        self._devices = []
        self.devices_initialized = False
        self._listeners = []

    async def run(self):
        if not self.devices_initialized:
            self._initialize_devices()

        coroutines = []
        for listener in self._listeners:
            coroutines.append(listener)
        for device in self._devices:
            coroutines.append(device.requests_runner())
        print(coroutines)
        try:
            self.loop.run_until_complete(asyncio.gather(*coroutines))
        except RuntimeError:
            await asyncio.gather(*coroutines)
        except Exception as e:
            print(e)
            raise e
        finally:
            print('terminating')
            self.zmq_context.term()

    def add_router(self, bind_to=None):
        self._listeners.append(router(self, bind_to=bind_to))

    def add_sub(self, connect_to=None, topics=None):
        self._listeners.append(sub(self, connect_to=connect_to, topics=topics))

    def add_device(self, api_key, device_class, *args, **kwargs):
        device = device_class(*args,
                              loop=self.loop,
                              **kwargs)
        self._devices.append(device)
        self.api_map[api_key] = device

    def api_register(self, name, device):
        if name in self.api_map:
            raise ValueError('Cannot register {}, already registered'.format(name))
        self.api_map[name] = device
        self.devices.append(device)

    def _initialize_devices(self):
        self.initialize_devices()
        self.devices_initialized = True

    def initialize_devices(self):
        raise NotImplementedError
