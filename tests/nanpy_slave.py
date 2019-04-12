#!/usr/bin/env python3

"""
Demonstration of a very generic Arkady interface to NanPy.

Direct dependencies are: arkady, nanpy
Indirect depencences are: pyserial, pyzmq
"""

from arkady import Application
from arkady.devices import SerialDevice

from nanpy import SerialManager, ArduinoApi

ARDUINO_PORT = '/dev/ttyUSB0'  # On Windows this is more like "COM3"


class GenericNanpy(SerialDevice):
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
            return 'Got a value that could not be treated as integer'
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
        if len(words) == 0:  # Check for empty message
            return 'ERROR: empty message!'
        key_word = words[0]
        if key_word not in word_map:  # Check if we recognize the first word
            return 'ERROR: not one of the known functions, {}'.format(word_map.keys())
        try:
            # Call the corresponding method
            return word_map[key_word](*words[1:])
        except:
            return 'ERROR: "{}" failed, maybe a bad message or connection'


class MyApplication(Application):
    def config(self):
        self.add_device('nanpy', ARDUINO_PORT, GenericNanpy)
        self.add_router(bind_to='tcp://*:5555')

MyApplication.run()
