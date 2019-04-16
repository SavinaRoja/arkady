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

The method ``config`` gets called during creation of the application and is a
good place to put registrations of listeners and (as we'll address in a moment)
components. ``add_router`` will set up a router listener for the application,
and we have explicitly passed ``bind_to='tcp://*:5555'`` which instructs the
added router to listen on port 5555 (this is also the default if you don't
specify).

This application alone won't do anything until we add at least one component
to it.

Creating a component
--------------------

The Nanpy interface has four main functions which we will wish to make accessible
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

In the ``__init__`` method we initialize the Nanpy ``ArduinoApi`` on the
specified port In the methods ``analog_read``, ``digital_read``,
``analog_write``, and ``digital_write`` we provide Nanpy functionality.

The next step is to write a message handler for the component. The application's
listeners will pass messages received along to this method.

.. code-block:: python

    class GenericNanpy(SerialComponent):

        ...

        def handler(self, msg, *args, **kwargs):
            """Handle an inbound message. Returned values go back as reply."""
            word_map = {
                'dwrite': self.digital_write,
                'awrite': self.analog_write,
                'dread': self.digital_read,
                'aread': self.analog_read,
            }
            words = msg.split()
            if len(words) < 2:  # Check for too short message
                return 'ERROR: message must contain at least 2 words!'
            key_word = words[0]
            try:
                pin = int(words[1])
            except ValueError:
                return 'ERROR: got non-int for pin number {}'.format(words[1])
            if key_word not in word_map:  # Check if we recognize the first word
                return 'ERROR: not one of the known functions, {}'.format(word_map.keys())
            try:
                # Call the corresponding method
                ret_val = word_map[key_word](pin, *words[2:])
                if ret_val is not None:
                    ret_val = str(ret_val)
                return ret_val
            except:
                return 'ERROR: "{}" failed, maybe a bad message or connection'.format(msg)

This ``handler`` method does the job of interpreting messages so that action may
be taken, along with some error handling. Care is taken to return the results of
the called methods, as the returned string values will get passed back to a
client of our Arkady application as the body of a reply message, this will be
addressed further below.

Now that our custom component has been implemented, we wish to add it to our
application and register it so that messages may be passed to it. Let's update
``my_application.py``:

.. code-block:: python
    :emphasize-lines: 10

    # my_application.py

    from arkady import Application

    ARDUINO_PORT = '/dev/ttyUSB0'  # On Windows this is more like "COM3"


    class MyApplication(Application):
        def config(self):
            self.add_component('nanpy', GenericNanpy, ARDUINO_PORT)
            self.add_router(bind_to='tcp://*:5555')

This addition to ``config`` tells the application that when the listeners
receive messages, if the first word of the message is "nanpy" then the message
should go to an instance of ``GenericNanpy``, created once for the application
with ``GenericNanpy(ARDUINO_PORT)``.

Now the application is completed, and here it is all together:

.. literalinclude:: ../tests/nanpy_slave.py

A Client for our Arkady Application
-----------------------------------

It should be noted, that because Arkady makes use of ZeroMQ, a client
can be written in nearly any language as bindings are widely implemented. The
following example is simply an example in Python using PyZMQ. It is interactive
so that you might test out sending arbitrary messages to your Arduino (via
Nanpy, via Arkady!).

.. literalinclude:: ../tests/nanpy_master.py

A Quick Guide to Setting up Nanpy
---------------------------------

Using Nanpy from your computer is as simple as:

.. code-block:: console

    pip install nanpy

To put the corresponding firmware on your Arduino, you can get a copy of this
firmware_ with the following command. These instructions are also outlined there.

.. code-block:: console

    git clone https://github.com/nanpy/nanpy-firmware.git

.. _firmware: https://github.com/nanpy/nanpy-firmware

Then change directories to the subsequent ``nanpy-firmware`` directory and
execute ``./configure.sh``. Then copy the ``nanpy-firmware/Nanpy`` directory
into your Arduino sketchbook directory.

Plug in your Arduino, start the Arduino IDE, configure your boardset and port,
open the Nanpy module from the sketchbook, and then Upload. Assuming everything
went well, your Arduino should be ready for Nanpy control.
