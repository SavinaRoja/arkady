# coding: utf-8

"""

"""

import asyncio
import zmq
import zmq.asyncio
from .listeners import router, sub


class Application(object):
    """
    The `Application` object represents the configurable whole of the an
    Arkady interface. Listeners are added for interprocess input and
    Components are added to handle that input. Components may implement communication
    with other Arkady applications via their listeners.
    """
    def __init__(self):
        """
        Initialization of the base `Application` takes no arguments.

        :return:
        """
        self.loop = asyncio.get_event_loop()
        self.zmq_context = zmq.asyncio.Context()
        self.component_key_map = {}
        self._components = []
        self._listeners = []
        self.config()

    def config(self):
        """
        Actions to be performed on initialization of the `Application`.

        It does nothing in the base class and is meant to be overridden to add
        on new functionality to deriving `Applications`.
        """
        pass

    def add_router(self, bind_to=None):
        """
        Creates and configures a router-type listener for the `Application`
        for use in Request-Reply (REQ-REP) communication.

        The router socket binds to a port and listens for input of requests
        (`zmq.REQ`). The first word of the request is taken as a component name
        to send the message to the appropriate component handler. The value
        returned from the component handler is returned as a reply (`zmq.REP` to
        the original requester.

        Unless you have reasons to use another type of listener, this is likely
        the one that you want. Implementation, and further documentation, is in
        `arkady.listeners`

        :param bind_to: A network string such as 'tcp://*:5555'
        :type bind_to: str
        """
        self._listeners.append(router(self, bind_to=bind_to))

    def add_sub(self, connect_to=None, topics=None):
        """
        Creates and configures a subscriber-type listener for the `Application`
        for use in Publisher-Subscriber (PUB-SUB) communication.

        The subscriber socket connects to a port (whether local or remote) and
        listens (`zmq.SUB`) for messages to be published (`zmq.PUB`). The
        subscriber can be configured with topics: strings against which the
        start of a published message must match. If no topics are specified, the
        subscriber will gather any published message on the socket. No reply is
        sent in PUB-SUB communication.

        If you wish to broadcast to none or more subscribers, with no need for
        reply or acknowledment of receipt, then PUB-SUB may be right for you.
        Implementation, and further documentation, is in`arkady.listeners`

        :param connect_to: A network string such as 'tcp://localhost:5555'
        :type connect_to: str
        :param topics: A list of topic strings such as ['light', 'action']
        :type topics: [str]
        """
        self._listeners.append(sub(self, connect_to=connect_to, topics=topics))

    def run(self):
        """
        """
        if not self.component_key_map:
            raise ApplicationConfigError('Application component_key_map is empty')

        if not self._listeners:
            raise ApplicationConfigError('Application has no listeners')

        coroutines = []
        for listener in self._listeners:
            coroutines.append(listener)
        for component in self._components:
            coroutines.append(component.requests_runner())
        try:
            self.loop.run_until_complete(asyncio.gather(*coroutines))
        finally:
            print('terminating')
            self.zmq_context.term()

    def add_component(self, name: str, component_class, *args, **kwargs):
        component = component_class(*args,
                                    loop=self.loop,
                                    **kwargs)
        self._components.append(component)
        self.component_key_map[name] = component

    def api_register(self, name, component):
        if name in self.component_key_map:
            raise ValueError('Cannot register {}, already registered'.format(name))
        self.component_key_map[name] = component
        self.components.append(component)


class ApplicationConfigError(Exception):
    pass
