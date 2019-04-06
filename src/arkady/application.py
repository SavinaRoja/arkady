# coding: utf-8

"""
DeviceAPI.application provides the framework for creating a DeviceAPI
Application.
"""

import asyncio
import zmq
import zmq.asyncio
from .listeners import sub


class Application(object):
    """

    """

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.zmq_context = zmq.asyncio.Context()
        self.api_map = {}
        self.devices = []
        self.devices_initialized = False

    def run(self):
        """

        :return:
        """
        coroutines = [sub(self.zmq_context,
                          self.api_map,
                          #connect_to='tcp://127.0.0.1:5555'
                          )]
        try:
            self.loop.run_until_complete(asyncio.gather(*coroutines))
        except Exception as e:
            print(e)
            raise e
        finally:
            print('terminating')
            self.zmq_context.term()
