from arkady import Application
from arkady.devices import AsyncDevice, SerialDevice

import asyncio
import time


class MyDevice(AsyncDevice):
    async def handler(self, msg, *args, **kwargs):
        # Doing some longer work
        print(msg)
        await asyncio.sleep(1)
        res = await asyncio.gather(
            self.sub_handler(msg),
            self.sub_handler(msg),
            self.sub_handler(msg)
        )
        print(res)
        return '{} done'.format(res)

    async def sub_handler(self, msg):
        await asyncio.sleep(1)
        res = await asyncio.gather(
            self.sub_sub_handler(msg),
            self.sub_sub_handler(msg),
        )
        return res

    async def sub_sub_handler(self, msg):
        await asyncio.sleep(1)
        return msg


class MyApp(Application):
    def config(self):
        self.add_router(bind_to='tcp://*:5555')
        self.add_device(MyDevice, 'test')


MyApp().run()