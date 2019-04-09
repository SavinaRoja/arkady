from arkady.application import Application
from arkady.devices import DummySerialDevice, DummyAsyncDevice

import asyncio
import concurrent.futures


class RouterApplication(Application):
    router_port = 5555

    def __init__(self, *args, **kwargs):
        super(RouterApplication, self).__init__(*args, **kwargs)
        self.add_router(bind_to='tcp://*:{}'.format(self.router_port))

    def initialize_devices(self):
        self.add_device('serial', DummySerialDevice)
        self.add_device('async', DummyAsyncDevice)


class SubApplication(Application):
    sub_port = 5556

    def __init__(self, *args, **kwargs):
        super(SubApplication, self).__init__(*args, **kwargs)
        self.add_router(bind_to='tcp://*:{}'.format(self.router_port))

    def initialize_devices(self):
        self.add_device('serial', DummySerialDevice)
        self.add_device('async', DummyAsyncDevice)


class DualApplication(Application):
    router_port = 5557
    sub_port = 5558

    def __init__(self, *args, **kwargs):
        super(DualApplication, self).__init__(*args, **kwargs)
        self.add_router(bind_to='tcp://*:{}'.format(self.router_port))

    def initialize_devices(self):
        self.add_device('serial', DummySerialDevice)
        self.add_device('async', DummyAsyncDevice)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # def simple_main():
    #RouterApplication().run()


    # async def main():
    #     await asyncio.gather(
    #         loop.run_in_executor(None, RouterApplication(loop=loop).run),
    #         # loop.run_in_executor(pool, SubApplication().run),
    #         # loop.run_in_executor(pool, DualApplication().run),
    #     )
    loop.run_until_complete(RouterApplication().run())
