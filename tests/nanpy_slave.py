#!/usr/bin/env python3

"""
Demonstration of a very generic Arkady interface to NanPy.

Direct dependencies are: arkady, nanpy
Indirect depencences are: pyserial, pyzmq
"""

from arkady import Application
from arkady.components import SerialComponent

from nanpy import SerialManager, ArduinoApi

ARDUINO_PORT = '/dev/ttyUSB0'  # On Windows this is more like "COM3"


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


class MyApplication(Application):
    def config(self):
        self.add_device('nanpy', GenericNanpy, ARDUINO_PORT)
        self.add_router(bind_to='tcp://*:5555')

MyApplication().run()
