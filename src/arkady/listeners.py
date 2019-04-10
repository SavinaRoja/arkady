# coding: utf-8

"""
"""

import asyncio
import zmq
import zmq.asyncio


async def router(application, bind_to=None):
    """
    The ``router`` listener handles asynchronous requests in the request-reply
    pattern. A request of type `zmq.REQ` shall be given a reply of type `zmq.REP`

    :param application:
    :param bind_to: Network path on which to listen. Defaults to ``'tcp://*:5555'``
    :type bind_to: string
    :return:
    """

    if bind_to is None:
        bind_to = 'tcp://*:5555'

    loop = asyncio.get_event_loop()

    rsock = application.zmq_context.socket(zmq.ROUTER)
    rsock.bind(bind_to)

    return_queue = asyncio.Queue()

    async def receive():
        while True:
            request = await rsock.recv_multipart()
            # Separate the header from the body of the message
            headers, body = request[0:2], request[2]
            body = body.decode('utf-8')
            # Separate the name from the msg to find the device to pass msg to
            name, msg = body.split(maxsplit=1)
            device = application.device_key_map[name]
            # Pass the header, msg, and return_queue to device for enqueuing
            loop.create_task(
                device._handler(
                    headers=headers,
                    msg=msg,
                    return_queue=return_queue
                )
            )

    async def transmit():
        while True:
            reply = await return_queue.get()
            # the reply should have the original headers prepended
            rsock.send_multipart(reply)

    try:
        await asyncio.gather(receive(), transmit())
    except Exception as e:
        raise e
    finally:
        rsock.close()
        # zmq_context.term()


async def sub(application, connect_to=None, topics=None):
    """
    The ``sub`` listener handles asynchronous requests in the pub-sub
    pattern. A request of type `zmq.PUB` receives no reply

    :param application:
    :param connect_to: A well-known network URI, like 'tcp://192.168.1.200:5555'
    :type connect_to: string
    :param topics: A list of topics as to subscribe to
    :type topics: [string]
    :return:
    """

    if topics is None:
        topics = ['']

    if connect_to is None:
        connect_to = 'tcp://localhost:5555'

    loop = asyncio.get_event_loop()

    ssock = application.zmq_context.socket(zmq.SUB)

    for topic in topics:
        ssock.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))

    ssock.connect(connect_to)

    while True:
        pub = await ssock.recv_multipart()
        topic, body = pub[0], pub[1]
        topic, body = topic.decode('utf-8'), body.decode('utf-8')
        name, msg = body.split(maxsplit=1)
        device = application.device_key_map[name]
        # Pass the msg, and return_queue to device for enqueuing
        loop.create_task(device._handler(topic=topic, msg=msg))
