from arkady.application import Application
from arkady.devices import DummySerialDevice, DummyAsyncDevice

import multiprocessing


class RouterApplication(Application):
    router_port = 5555

    def config(self):
        self.add_router(bind_to='tcp://*:{}'.format(self.router_port))
        self.add_device(DummySerialDevice, 'serial')
        self.add_device(DummyAsyncDevice, 'async')


class SubApplication(Application):
    sub_port = 5556

    def config(self):
        self.add_sub(connect_to='tcp://localhost:{}'.format(self.sub_port), topics=['test'])
        self.add_device(DummySerialDevice, 'serial')
        self.add_device(DummyAsyncDevice, 'async')


class DualApplication(Application):
    router_port = 5557
    sub_port = 5558

    def config(self):
        self.add_router(bind_to='tcp://*:{}'.format(self.router_port))
        self.add_sub(connect_to='tcp://localhost:{}'.format(self.sub_port), topics=['test'])
        self.add_device(DummySerialDevice, 'serial')
        self.add_device(DummyAsyncDevice, 'async')


def a0():
    RouterApplication().run()


def a1():
    SubApplication().run()


def a2():
    DualApplication().run()


if __name__ == '__main__':
    p0 = multiprocessing.Process(target=a0)
    p1 = multiprocessing.Process(target=a1)
    p2 = multiprocessing.Process(target=a2)
    p0.start()
    p1.start()
    p2.start()
    p0.join()
    p1.join()
    p2.join()

