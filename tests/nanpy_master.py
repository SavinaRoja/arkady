#!/usr/bin/env python3

"""
Demonstration of a program controllering the very generic Arkady interface to
NanPy.

Direct dependencies are: pyzmq
"""

import zmq

context = zmq.Context()
sock = zmq.socket(zmq.REQ)
sock.connect('tcp://localhost:5555')

while True:
    msg = input('Send a message to the Nanpy device: ')
    sock.send_string('nanpy ' + msg)
    print('Waiting for reply.')
    reply = sock.recv_string()
    print('Got: ' + reply)
