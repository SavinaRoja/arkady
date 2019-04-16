Getting Started with Arkady
===========================

The first step in working with Arkady is to think about what "action" you wish
to make available for networked (websocket from another machine) or simply
interprocess control. Let's start with something simple and accessible, a
generic interface to Nanpy, all you need to work along is an Arduino.

Nanpy_ is a great prototyping tool that lets you interface with an Arduino over
a serial connection to control and read pins. Setup and usage will be
covered in more detail below.

.. _nanpy: https://github.com/nanpy/nanpy

Choosing a listener
-------------------

A listener is responsible for "listening" for external input, and at present
there are two in Arkady: ``router`` and ``sub``. The `router` handles asynchronous
request-reply interaction and is best to use when you need to return information
to a requester, or at least provide acknowledgment of receipt. The `sub` handles
publish-subscribe type interaction which is a one-way kind of communication.

Because Nanpy permits reading the value of a pin, and I'll want to be able to
send this data back to a requester, I'm going to add a router to my Arkady
Application.

.. code-block:: python

    # my_application.py

    from arkady import Application

    class MyApplication(Application):
        def config(self):
            self.add_router(bind_to='tcp://*:5555')

::

The method ``config`` gets called during creation of the application and is a
good place to put registrations of listeners and (as we'll address in a moment)
components. ``add_router`` will set up a router listener for the application,
and I have explicitly passed ``bind_to='tcp://*:5555'`` which instructs the
added router to listen on port 5555 (this is also the default if you don't
specify).

This application alone won't do anything until we add at least one component
to it.

Creating a component
--------------------

The Nanpy interface has four main functions which I will wish to make accessible
through the application: ``digitalRead``, ``analogRead``, ``digitalWrite``, and
``analogWrite``. So let's create a component that implements those actions.

There are two central base components in Arkady from which to derive:
``SerialComponent`` and ``AsyncComponent``. Arkady handles concurrency so it's
possible for more than one message to come in for a component and run
simultaneously. This can be a problem in some cases, as in this case where we
should only allow one message exchange over the USB to the Arduino at one time.
So we'll choose ``SerialComponent`` which ensures serial (not concurrent)
execution of jobs.

.. code-block:: python

    from arkady.components import SerialComponent
    from nanpy import SerialManager, ArduinoApi


    class GenericNanpy(SerialComponent):
        def __init__(self, port, *args, **kwargs):
            super(GenericNanpy, self).__init__(*args, **kwargs)
            self._serial_manager = SerialManager(device=port, baudrate=115200)
            self.ardu = ArduinoApi(self._serial_manager)

        def analog_read(self, pin_number, *_words):
            """Read the pin in analog mode"""
            self.ardu.pinMode(pin_number, self.ardu.INPUT)
            return self.ardu.analogRead(pin_number)

        def digital_read(self, pin_number, *_words):
            """Read the pin in digital mode"""
            self.ardu.pinMode(pin_number, self.ardu.INPUT)
            return self.ardu.digitalRead(pin_number)

        def analog_write(self, pin_number, value, *_words):
            """Write the pin in analog mode to value"""
            try:
                value = int(value)
            except ValueError:
                return 'ERROR: Got a value that could not be treated as integer'
            self.ardu.pinMode(pin_number, self.ardu.OUTPUT)
            self.ardu.analogWrite(pin_number, value)

        def digital_write(self, pin_number, value, *_words):
            """Write the pin HIGH if value is 'high' otherwise LOW."""
            self.ardu.pinMode(pin_number, self.ardu.OUTPUT)
            if value == 'high':
                self.ardu.digitalWrite(pin_number, self.ardu.HIGH)
            else:
                self.ardu.digitalWrite(pin_number, self.ardu.LOW)

::

A Quick Guide to Setting up Nanpy
---------------------------------

