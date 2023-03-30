from abc import ABC, abstractmethod, abstractproperty
import pyfirmata
import time
import random
import RPi.GPIO as GPIO

class MCU(ABC):
    def __init__(self, com_port, led_pins, button_pins, switch_pin):
        self.led_pins = led_pins
        self.button_pins = button_pins
        self.switch_pin = switch_pin
        self.com_port = com_port


    @abstractmethod
    def turn_on_led(led_pin):
        pass

    @abstractmethod
    def turn_off_led(led_pin):
        pass

    def turn_on_leds(self):
        for led_pin in self.led_pins:
            self.turn_on_led(led_pin)

    def turn_off_leds(self):
        for led_pin in self.led_pins:
            self.turn_off_led(led_pin)

    @abstractmethod
    def get_button_state(button_pin):
        pass

    def get_button_states(self):
        button_states = []

        for button_pin in self.button_pins:
            button_states.append(self.get_button_state(button_pin))

        return button_states

    @abstractmethod
    def get_switch_state(switch_pin):
        pass

class Arduino(MCU):
    def __init__(self, com_port, led_pins, button_pins, switch_pin):
        super().__init__(com_port, led_pins, button_pins, switch_pin)
        
        if com_port:
            self.board = pyfirmata.Arduino(com_port)
        else:
        self.board = pyfirmata.Arduino('COM7')
        
        it = pyfirmata.util.Iterator(self.board)
        it.start()

        self.leds = {}
        for led_pin in self.led_pins:
            led = self.board.digital[led_pin]
            led.mode = pyfirmata.OUTPUT
            self.leds[led_pin] = led

        self.buttons = {}
        for button_pin in self.button_pins:
            button = self.board.digital[button_pin]
            button.mode = pyfirmata.INPUT
            self.buttons[button_pin] = button

        self.switch = self.board.digital[switch_pin]
        self.switch.mode = pyfirmata.INPUT

    def turn_on_led(self, led_pin):
        self.leds[led_pin].write(1)
    
    def turn_off_led(self, led_pin):
        self.leds[led_pin].write(0)

    def get_button_state(self, button_pin):
        return self.buttons[button_pin].read()
    
    def get_switch_state(self, _):
        return self.switch.read()


class RPi(MCU):
    def __init__(self, com_port, led_pins, button_pins, switch_pin):
        super().__init__(com_port, led_pins, button_pins, switch_pin)
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.switch_pin, GPIO.IN)
        GPIO.setup(self.button_pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.led_pins, GPIO.OUT)

    def turn_on_led(self, led_pin):
        GPIO.output(led_pin, GPIO.HIGH)
    
    def turn_off_led(self, led_pin):
        GPIO.output(led_pin, GPIO.LOW)

    def get_button_state(self, button_pin):
        return GPIO.input(button_pin) == GPIO.HIGH
    
    def get_switch_state(self, switch_pin):
        return GPIO.input(switch_pin) == GPIO.HIGH
