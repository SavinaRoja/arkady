#!/usr/bin/env python3

"""
Demonstration of a program controlling the very generic Arkady interface to
NanPy.

Direct dependencies are: pyzmq
"""

import zmq

NANPY_ADRRESS = 'tcp://localhost:5555'  # replace localhost with IP if remote

context = zmq.Context()
sock = context.socket(zmq.REQ)
sock.connect(NANPY_ADRRESS)

while True:
    msg = input('Send a message to the Nanpy device: ')
    sock.send_string('nanpy ' + msg)
    print('Waiting for reply.')
    reply = sock.recv_string()
    print('Got: ' + reply)
