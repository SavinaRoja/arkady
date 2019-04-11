import asyncio
import zmq
import zmq.asyncio
import time

context = zmq.asyncio.Context()


async def query(msg):
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:5555')
    await socket.send_string('test {}'.format(msg))
    reply = await socket.recv_string()
    return reply

loop = asyncio.get_event_loop()

start = time.time()
messages = 'this is an ex parrot'.split()
queries = [query(msg) for msg in messages]
# loop.run_until_complete(query('help'))
results = loop.run_until_complete(asyncio.gather(*queries))
print('Execution time: {}'.format(time.time()-start))
print(results)
